"""Named lifecycles for the delegation bench (one place, no free-text states).

Two machines live here. Both were previously implicit: spelled as bare
strings or re-derived by copy-pasted loops in every bench script.

1. VERDICT - the pre-registered decision table (DESIGN.md section 5).
   The stored values are the exact strings already on disk in
   raw-results.jsonl (``["RED", "screen <=2/5"]`` etc.), so ``Verdict`` is a
   ``StrEnum``: ``Verdict.RED == "RED"`` and ``json.dumps`` writes ``"RED"``.

   Verdicts are DERIVED from an append-only list of trial outcomes; appending
   one more trial may only move along these edges::

       INCOMPLETE --> INCOMPLETE | RED | YELLOW | ESCALATE | CAPABILITY-GREEN-CANDIDATE
       ESCALATE   --> INCOMPLETE                      (full n=15 under way)
       YELLOW     --> INCOMPLETE | YELLOW             (screen 3-4/5 -> full run;
                                                       full 13-14/15 is final)
       RED        --> RED                             (final)
       CAPABILITY-GREEN-CANDIDATE --> CAPABILITY-GREEN-CANDIDATE   (confirmation pending)
                                    | CAPABILITY-GREEN | AUTONOMY-GREEN
       CAPABILITY-GREEN --> CAPABILITY-GREEN          (final)
       AUTONOMY-GREEN   --> AUTONOMY-GREEN            (final)

2. CELL LEDGER - resume state of one cell inside an append-only results
   .jsonl (rows ``{"cell", "trial", ...}``). The on-disk format is unchanged:
   a run ("segment") is a block of rows whose ``trial`` counts 1, 2, 3, ...;
   a new segment starts when ``trial`` goes back to 1. The full_bench scripts
   stack a screen segment (n=5) and then a fresh escalation segment of n=N
   (that is how the published cards reach n=20 / n=25). The walk-away script
   keeps ONE continuous segment. Per cell, for a requested size N::

       FRESH --start--> SCREENING --(len reaches SCREEN_N)--> SCREENED
       SCREENED --(N > SCREEN_N: start)--> ESCALATING --(len reaches N)--> ESCALATED

   A run interrupted mid-segment RESUMES that segment at ``last + 1``; it
   never restarts at trial 1 (the old copies did, which double-counted
   aborted trials - see results/full-bench-8ba1b-mac-2026-08-26.jsonl C2-M).
"""
from enum import StrEnum

SCREEN_N = 5      # design section 5: screen n=5
FULL_N = 15       # full n=15 (also the confirmation size)


class Verdict(StrEnum):
    RED = "RED"
    YELLOW = "YELLOW"
    ESCALATE = "ESCALATE"
    INCOMPLETE = "INCOMPLETE"
    CAPABILITY_GREEN_CANDIDATE = "CAPABILITY-GREEN-CANDIDATE"
    CAPABILITY_GREEN = "CAPABILITY-GREEN"
    AUTONOMY_GREEN = "AUTONOMY-GREEN"


V = Verdict
VERDICT_TRANSITIONS = {
    V.INCOMPLETE: frozenset({V.INCOMPLETE, V.RED, V.YELLOW, V.ESCALATE,
                             V.CAPABILITY_GREEN_CANDIDATE}),
    V.ESCALATE: frozenset({V.INCOMPLETE}),
    V.YELLOW: frozenset({V.INCOMPLETE, V.YELLOW}),
    V.RED: frozenset({V.RED}),
    V.CAPABILITY_GREEN_CANDIDATE: frozenset({V.CAPABILITY_GREEN_CANDIDATE,
                                             V.CAPABILITY_GREEN, V.AUTONOMY_GREEN}),
    V.CAPABILITY_GREEN: frozenset({V.CAPABILITY_GREEN}),
    V.AUTONOMY_GREEN: frozenset({V.AUTONOMY_GREEN}),
}
FINAL_VERDICTS = frozenset(v for v, nxt in VERDICT_TRANSITIONS.items() if nxt == {v})


class IllegalTransition(ValueError):
    pass


def parse_verdict(value):
    """Tolerant reader for a stored verdict: accepts the enum, the stored
    string, or the stored ``[verdict, why]`` pair. Unknown -> ValueError."""
    if isinstance(value, (list, tuple)):
        value = value[0]
    return Verdict(str(value).strip().upper())


def check_verdict_transition(old, new):
    """Raise IllegalTransition unless old -> new is a legal edge."""
    old, new = Verdict(old), Verdict(new)
    if new not in VERDICT_TRANSITIONS[old]:
        raise IllegalTransition(f"verdict {old} -> {new} is not a legal move")
    return new


def screen_verdict(passes):
    """Screen stage (first SCREEN_N trials). Returns (Verdict, why).
    Fewer than SCREEN_N trials is INCOMPLETE unless already decided RED
    (3+ failures make <=2/5 certain)."""
    n5 = [bool(p) for p in passes[:SCREEN_N]]
    k, fails = sum(n5), len(n5) - sum(n5)
    if fails > SCREEN_N - 3:
        return V.RED, f"screen <={SCREEN_N - 3}/{SCREEN_N}"
    if len(n5) < SCREEN_N:
        return V.INCOMPLETE, f"screen {len(n5)}/{SCREEN_N} trials"
    if k == SCREEN_N:
        return V.ESCALATE, f"screen {SCREEN_N}/{SCREEN_N} - escalate to n={FULL_N}"
    return V.YELLOW, f"screen 3-4/{SCREEN_N} (confirmation pending)"


def decide(trial_passes, confirmation_passes=None):
    """The single decision table. trial_passes: list of bool (screen then
    full merged, in order). confirmation_passes: the fresh confirmation run.
    Returns (Verdict, why); the pair is what raw-results.jsonl stores."""
    trial_passes = [bool(p) for p in trial_passes]
    sv, why = screen_verdict(trial_passes)
    if sv in (V.RED, V.INCOMPLETE):
        return sv, why
    if len(trial_passes) == SCREEN_N:
        return sv, why                      # YELLOW or ESCALATE, screen only
    n15 = trial_passes[:FULL_N]
    if len(n15) < FULL_N:
        return V.INCOMPLETE, f"{len(n15)}/{FULL_N} trials"
    p15 = sum(n15)
    if p15 <= FULL_N - 3:
        return V.RED, f"{p15}/{FULL_N}"
    if p15 < FULL_N:
        return V.YELLOW, f"{p15}/{FULL_N}"
    # 15/15: capability-green candidate; autonomy needs a clean confirmation 15
    if confirmation_passes is None:
        return V.CAPABILITY_GREEN_CANDIDATE, f"{FULL_N}/{FULL_N}; confirmation run required"
    conf = [bool(p) for p in confirmation_passes[:FULL_N]]
    kc = sum(conf)
    if kc < len(conf):
        return (V.CAPABILITY_GREEN,
                f"{FULL_N}/{FULL_N} first run; confirmation {kc}/{FULL_N} (autonomy not earned)")
    if len(conf) < FULL_N:
        return (V.CAPABILITY_GREEN_CANDIDATE,
                f"{FULL_N}/{FULL_N}; confirmation {kc}/{len(conf)} so far (pending)")
    return V.AUTONOMY_GREEN, f"{2 * FULL_N}/{2 * FULL_N}"


# ---------------------------------------------------------------- ledger ---

class CellPhase(StrEnum):
    FRESH = "fresh"            # no rows yet
    SCREENING = "screening"    # screen segment shorter than SCREEN_N
    SCREENED = "screened"      # screen segment complete, no escalation yet
    ESCALATING = "escalating"  # escalation segment shorter than its target
    ESCALATED = "escalated"    # escalation segment complete


def segments(trials):
    """Split a cell's stored trial numbers into runs. Tolerant of legacy
    data: any row whose trial is not ``prev + 1`` starts a new segment."""
    segs = []
    for t in trials:
        t = int(t)
        if segs and t == segs[-1][-1] + 1:
            segs[-1].append(t)
        else:
            segs.append([t])
    return segs


class CellLedger:
    """Resume state for one cell. ``screen_n=None`` means a single
    continuous segment (walk-away tier); otherwise screen then escalation."""

    def __init__(self, trials=(), screen_n=SCREEN_N):
        self.screen_n = screen_n
        self.trials = [int(t) for t in trials]

    @classmethod
    def from_rows(cls, rows, cell, screen_n=SCREEN_N):
        return cls([r.get("trial", 0) for r in rows if r.get("cell") == cell], screen_n)

    def _split(self):
        """Return (segments, screen index or None, escalation index or None).
        Segments before the first one that reaches screen_n are aborted
        screen attempts (legacy) and are ignored for planning."""
        segs = segments(self.trials)
        if not segs:
            return segs, None, None
        last = len(segs) - 1
        if self.screen_n is None:
            return segs, None, last
        for i, s in enumerate(segs):
            if len(s) >= self.screen_n:
                return segs, i, (last if i < last else None)
        return segs, last, None

    def _parts(self):
        segs, si, ei = self._split()
        return (segs[si] if si is not None else None,
                segs[ei] if ei is not None else None)

    def phase(self, n):
        screen, esc = self._parts()
        if self.screen_n is None:
            if esc is None:
                return CellPhase.FRESH
            return CellPhase.ESCALATED if len(esc) >= n else CellPhase.ESCALATING
        if screen is None:
            return CellPhase.FRESH
        if len(screen) < self.screen_n:
            return CellPhase.SCREENING
        if esc is None:
            return CellPhase.SCREENED
        return CellPhase.ESCALATED if len(esc) >= n else CellPhase.ESCALATING

    def pending(self, n):
        """The trial numbers still to run for size n, in order (empty = done)."""
        ph = self.phase(n)
        screen, esc = self._parts()
        if self.screen_n is None:
            last = 0 if esc is None else esc[-1]
            return list(range(last + 1, n + 1))
        screen_target = min(n, self.screen_n)
        if ph is CellPhase.FRESH:
            return list(range(1, screen_target + 1))
        if ph is CellPhase.SCREENING:
            return list(range(screen[-1] + 1, screen_target + 1))
        if ph is CellPhase.SCREENED:
            return list(range(1, n + 1)) if n > self.screen_n else []
        if ph is CellPhase.ESCALATING:
            return list(range(esc[-1] + 1, n + 1))
        return []

    def record(self, trial, n):
        """The one write transition: append ``trial``. Refuses any trial
        that is not the next pending one for size n."""
        nxt = self.pending(n)
        if not nxt or int(trial) != nxt[0]:
            raise IllegalTransition(
                f"trial {trial} not legal in phase {self.phase(n)} (next: {nxt[:1] or 'none'})")
        self.trials.append(int(trial))
        return self

    def screen_passes(self, rows):
        """ok flags of the screen segment, aligned with stored rows."""
        return self._segment_rows(rows, which="screen")

    def _segment_rows(self, rows, which):
        segs, si, ei = self._split()
        idx = si if which == "screen" else ei
        if idx is None:
            return []
        start = sum(len(s) for s in segs[:idx])
        return [bool(r.get("ok")) for r in rows[start:start + len(segs[idx])]]


def summary_line(cell, cell_rows, screen_n=SCREEN_N):
    """Screen-summary line for a cell. Old copies printed ``{k}/5`` with k
    counted over EVERY row (escalated cells showed '25/5 YELLOW')."""
    led = CellLedger([r.get("trial", 0) for r in cell_rows], screen_n)
    oks = [bool(r.get("ok")) for r in cell_rows]
    sv, _ = screen_verdict(led.screen_passes(cell_rows))
    w = sorted(r["wall_ms"] for r in cell_rows)
    walls = f"{w[0]:.0f}/{w[len(w)//2]:.0f}/{w[-1]:.0f} ms" if w else "-/-/- ms"
    k5 = sum(led.screen_passes(cell_rows))
    return f"{cell:10s} {sum(oks)}/{len(oks)} screen {k5}/{screen_n} {sv:9s} {walls}"
