#!/usr/bin/env python3
"""Self-tests for bench/lifecycle.py: the named Verdict ladder and the
per-cell resume ledger. Exhaustive over both enums (a new state without a
row here fails), every legal / illegal move, legacy files on disk, the bugs
the old copy-pasted code had, and a seeded random stateful model test
(stdlib only, like the rest of this suite). PATTERN: no GPU, no network."""
import collections, glob, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bench"))
from lifecycle import (Verdict, VERDICT_TRANSITIONS, FINAL_VERDICTS, IllegalTransition,
                       parse_verdict, check_verdict_transition, screen_verdict, decide,
                       CellPhase, CellLedger, segments, summary_line, SCREEN_N)
import runner

PASS = FAIL = 0
def ck(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1; print(f"PASS {name}")
    else:
        FAIL += 1; print(f"FAIL {name}: got {got!r} want {want!r}")

def raises(fn):
    try:
        fn()
    except IllegalTransition:
        return True
    return False

T, F = True, False
RESULTS = os.path.join(HERE, "..", "results")

# --- verdict enum: exhaustive + byte-compatible stored values ---
STORED = {"RED", "YELLOW", "ESCALATE", "INCOMPLETE", "CAPABILITY-GREEN-CANDIDATE",
          "CAPABILITY-GREEN", "AUTONOMY-GREEN"}
ck("verdict-values-unchanged", {v.value for v in Verdict}, STORED)
ck("verdict-every-state-has-edges", set(VERDICT_TRANSITIONS), set(Verdict))
ck("verdict-json-compatible", json.dumps(list(decide([T] * 5))),
   '["ESCALATE", "screen 5/5 - escalate to n=15"]')
ck("verdict-finals", FINAL_VERDICTS,
   {Verdict.RED, Verdict.CAPABILITY_GREEN, Verdict.AUTONOMY_GREEN})
ck("runner-reexports-decide", runner.decide is decide, True)
for v in Verdict:
    ck(f"parse-{v}", parse_verdict(v.value), v)
    ck(f"parse-pair-{v}", parse_verdict([v.value, "why"]), v)
ck("parse-lowercase-legacy", parse_verdict(" red "), Verdict.RED)
try:
    parse_verdict("GREEN"); ck("parse-unknown-refused", False, True)
except ValueError:
    ck("parse-unknown-refused", True, True)

# --- every legal edge accepted, every illegal edge refused (exhaustive) ---
for a in Verdict:
    for b in Verdict:
        legal = b in VERDICT_TRANSITIONS[a]
        ck(f"edge {a}->{b}", not raises(lambda: check_verdict_transition(a, b)), legal)

# --- derived state table: one row per verdict (exhaustive) ---
TABLE = [
    ([], None, Verdict.INCOMPLETE),
    ([T] * 4, None, Verdict.INCOMPLETE),
    ([F] * 3, None, Verdict.RED),
    ([T] * 2 + [F] * 3, None, Verdict.RED),
    ([T] * 3 + [F] * 2, None, Verdict.YELLOW),
    ([T] * 5, None, Verdict.ESCALATE),
    ([T] * 10, None, Verdict.INCOMPLETE),
    ([T] * 12 + [F] * 3, None, Verdict.RED),
    ([T] * 13 + [F] * 2, None, Verdict.YELLOW),
    ([T] * 15, None, Verdict.CAPABILITY_GREEN_CANDIDATE),
    ([T] * 15, [T] * 7, Verdict.CAPABILITY_GREEN_CANDIDATE),
    ([T] * 15, [T] * 14 + [F], Verdict.CAPABILITY_GREEN),
    ([T] * 15, [T] * 15, Verdict.AUTONOMY_GREEN),
]
for trials, conf, want in TABLE:
    ck(f"table {sum(trials)}/{len(trials)} conf={conf and f'{sum(conf)}/{len(conf)}'}",
       decide(trials, conf)[0], want)
ck("table-covers-every-verdict", {w for _, _, w in TABLE}, set(Verdict))

# --- BUG 1: partial screen. Old decide([F, F]) said RED but decide([T]*4)
# said INCOMPLETE; RED is only certain after 3 failures. ---
ck("bug1-partial-screen-2-fails-not-red", decide([F, F])[0], Verdict.INCOMPLETE)
ck("bug1-empty-not-red", decide([])[0], Verdict.INCOMPLETE)
ck("bug1-3-fails-is-red-early", decide([F, T, F, F])[0], Verdict.RED)
ck("screen-verdict-matches-decide", screen_verdict([T] * 5)[0], decide([T] * 5)[0])

# --- BUG 2: confirmation with more than 15 trials. Old code checked
# sum(conf) == 15, so 1 failure + 15 passes earned AUTONOMY-GREEN. ---
ck("bug2-conf-failure-not-autonomy", decide([T] * 15, [F] + [T] * 15)[0], Verdict.CAPABILITY_GREEN)

# --- BUG 3: an unfinished confirmation run was final CAPABILITY-GREEN,
# then flipped to AUTONOMY-GREEN once complete (a final verdict moving). ---
ck("bug3-partial-conf-pending", decide([T] * 15, [T] * 10)[0], Verdict.CAPABILITY_GREEN_CANDIDATE)
ck("bug3-partial-conf-with-fail-final", decide([T] * 15, [T] * 3 + [F])[0], Verdict.CAPABILITY_GREEN)

# --- ledger: segments + phase table (exhaustive over CellPhase) ---
ck("segments-split-on-reset", segments([1, 2, 3, 1, 2]), [[1, 2, 3], [1, 2]])
ck("segments-legacy-gap", segments([1, 2, 5]), [[1, 2], [5]])
seq = lambda *ns: [t for n in ns for t in range(1, n + 1)]
PHASES = [
    ([], 5, CellPhase.FRESH, [1, 2, 3, 4, 5]),
    (seq(3), 5, CellPhase.SCREENING, [4, 5]),
    (seq(5), 5, CellPhase.SCREENED, []),
    (seq(5), 20, CellPhase.SCREENED, list(range(1, 21))),
    (seq(5, 7), 20, CellPhase.ESCALATING, list(range(8, 21))),
    (seq(5, 20), 20, CellPhase.ESCALATED, []),
]
for trials, n, ph, todo in PHASES:
    led = CellLedger(trials)
    ck(f"phase {segments(trials) and [len(s) for s in segments(trials)]} N={n}", led.phase(n), ph)
    ck(f"pending {[len(s) for s in segments(trials)]} N={n}", led.pending(n), todo)
ck("phase-table-covers-every-phase", {p for _, _, p, _ in PHASES}, set(CellPhase))
ck("small-N-screen-stops-at-N", CellLedger([]).pending(3), [1, 2, 3])
ck("small-N-then-full-screen", CellLedger(seq(3)).pending(5), [4, 5])
ck("continuous-fresh", CellLedger([], screen_n=None).pending(3), [1, 2, 3])
ck("continuous-resume", CellLedger(seq(7), screen_n=None).pending(15), list(range(8, 16)))
ck("continuous-done", CellLedger(seq(15), screen_n=None).phase(15), CellPhase.ESCALATED)

# --- illegal writes refused ---
ck("record-skip-refused", raises(lambda: CellLedger(seq(2)).record(4, 5)), True)
ck("record-restart-mid-screen-refused", raises(lambda: CellLedger(seq(2)).record(1, 5)), True)
ck("record-when-done-refused", raises(lambda: CellLedger(seq(5, 15)).record(16, 15)), True)
ck("record-legal", CellLedger(seq(5)).record(1, 15).trials, seq(5, 1))

# --- BUG 4: resume restarted an interrupted run at trial 1 (all copies of
# full_bench*.py). Proof on disk: 8ba1b C2-M stored trials 1-4, then 1-5. ---
ck("bug4-resume-continues", CellLedger(seq(4)).pending(5), [5])
# --- BUG 5: "done" compared ALL rows to N, so an escalation that died at
# trial 15 of 20 (5 screen + 15 = 20 rows) was skipped as complete. ---
ck("bug5-escalation-crash-not-done", CellLedger(seq(5, 15)).pending(20), [16, 17, 18, 19, 20])

# --- legacy files on disk read back as complete for the N they were run at ---
def load(name):
    return [json.loads(l) for l in open(os.path.join(RESULTS, name))]
for name, n, screen_n in [("full-bench-2026-08-22.jsonl", 15, SCREEN_N),
                          ("full-bench-regate-2026-08-25.jsonl", 20, SCREEN_N),
                          ("full-bench-8ba1b-mac-2026-08-26.jsonl", 5, SCREEN_N),
                          ("full-bench-lfm2.6b-2026-08-25.jsonl", 5, SCREEN_N),
                          ("walkaway-regate-2026-08-25.jsonl", 15, None)]:
    rows = load(name)
    open_cells = [c for c in sorted({r["cell"] for r in rows})
                  if CellLedger.from_rows(rows, c, screen_n).pending(n)]
    ck(f"legacy-{name}-complete-at-N={n}", open_cells, [])
mac = load("full-bench-8ba1b-mac-2026-08-26.jsonl")
ck("legacy-aborted-screen-ignored", CellLedger.from_rows(mac, "C2-M").screen_passes(
    [r for r in mac if r["cell"] == "C2-M"]), [r["ok"] for r in mac if r["cell"] == "C2-M"][4:])

# --- BUG 6: the screen summary printed k over ALL rows against /5 and
# picked the verdict from that, so perfect escalated cells read "25/5 YELLOW"
# (bench-regate0825.log). ---
rg = load("full-bench-regate-2026-08-25.jsonl")
line = summary_line("C1-S", [r for r in rg if r["cell"] == "C1-S"])
ck("bug6-summary-total", " 25/25 " in line, True)
ck("bug6-summary-screen-verdict", "screen 5/5 ESCALATE" in line, True)
ck("summary-empty-cell-no-crash", "0/0" in summary_line("X", []), True)

# --- stateful random model test: verdict machine ---
rng = random.Random(20261110)
for case in range(400):
    p = rng.choice([0.5, 0.8, 0.95, 1.0])
    trials, conf = [], None
    prev = decide(trials, conf)[0]
    for _ in range(40):
        if len(trials) < 15 or rng.random() < 0.3 and conf is None:
            trials.append(rng.random() < p)
        else:
            conf = (conf or []) + [rng.random() < p] if rng.random() < 0.9 else (conf or [])
        cur = decide(trials, conf)[0]
        try:
            check_verdict_transition(prev, cur)
        except IllegalTransition as e:
            ck(f"model-verdict-case{case}", str(e), "legal"); break
        prev = cur
    else:
        PASS += 1


# --- stateful random model test: ledger under crashes and escalations ---
def invocation(trials, n, crash_after):
    """One bench script run: resume per the ledger, crash after k writes."""
    led = CellLedger(trials)
    for done, i in enumerate(led.pending(n)):
        if done == crash_after:
            return False
        led.record(i, n)
        trials.append(i)
    return True

bad = 0
for case in range(400):
    trials = []
    for n in (5, rng.choice([15, 20, 25])):
        while not invocation(trials, n, rng.choice([None, None, 0, 1, 3, 7, 12])):
            pass
        segs = segments(trials)
        want = [5] if n == 5 else [5, n]
        if [len(s) for s in segs] != want or CellLedger(trials).pending(n):
            bad += 1
            print(f"FAIL model-ledger case{case} N={n}: {[len(s) for s in segs]}")
ck("model-ledger (400 random crash/resume histories)", bad, 0)

print(f"SELF-TEST: {PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
