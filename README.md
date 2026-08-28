# delegation-bench

## The Delegation Benchmark — a "safe to hand off my work" benchmark for local models

By [Kyanite Labs](https://kyanitelabs.tech) - the lab that serves Qwen 3.8 27B on a
$1,400 Strix Halo mini-PC and publishes every number with its methodology
([the stack repo](https://github.com/KyaniteLabs/qwen38-27b-strix-halo)).

PRE-REGISTRATION NOTICE: the design below was published BEFORE any run
(2026-08-21); nothing was tuned after the fact. Measurement has since landed —
see Status and the certified cards under `results/`; every raw log is in the
repo beside this file, exactly as promised here.

THE QUESTION IT ANSWERS: which of the operator's real jobs can be safely
delegated — consistently — to a local model (Qwen3.8-27B on a $1,400 Strix
Halo) running inside the actual product built around it (tokflint/tokpal)?
Not "is the model smart" — "can you hand it work and walk away."

WHY IT DOESN'T EXIST ELSEWHERE (per the research files beside this design):
the pieces exist — capability leaderboards, injection-safety suites, judge
protocols, freshness methods — but no published benchmark composes them into
a personal delegation decision with certified floors, a separate walk-away
(autonomy) tier, ask-quality scoring, and split-recovery tests for automatic
task decomposition. The ask-quality rubric has no standard form anywhere yet.

WHAT IS HERE:
- DESIGN.md — the full pre-registered design (v3.1): 9 job classes, size
  ladders, the single decision table with exact confidence floors printed on
  every result (15/15 = at least 82%; 30/30 = at least 90%), the computed
  honesty table (probability the test says green at any true skill level),
  blinded dual-judge protocol, hidden-test oracles, a sabotage safety cell,
  sealed holdouts with shelf life, and the four decomposition measurements.
- research/W1-W3 — the three sourced research passes (contamination and
  private-bench operations; statistics and oracle gaming; judging, safety
  precedent, decision evals). Every claim carries a named source and date.

WHAT WILL NEVER BE HERE: the sealed holdout set. We publish the sealing
method (hash-manifest before first run), never the contents — that is what
keeps our own green honest.

THREE-STAGE PUBLICATION: (1) this design, published before any run; (2) the
runner, open source with template fixtures and a fixture generator; (3) the
results and the operator's delegation card. All three stages have shipped —
see `results/` and `llms.txt`.

## License
MIT. The design is the artifact; the audit trail (internal review + external
audit + field research) is summarized in DESIGN.md's lineage block.

## Status
Stage 3 SHIPPED: 965 measured trials (495 certified 08-22 + 470 re-gate at
deeper n 08-25) across the 9 job classes and 29 cells. Read the certified
cards — `results/CARD-2026-08-22.md`, `results/FINAL-CARD-2026-08-22.md`,
`results/CARD-RE-GATE-2026-08-25.md` — and `llms.txt` for the full trial
accounting. The judge kit passed its golden-fixture calibration
(`judges/golden.json`, `tests/test_golden.py`) before scoring real runs. The
walk-away tier went 6/6 GREEN at 40/40 (92.8% floors); an 8B-A1B Mac-class
cross-model screen (08-26) went 28/70 and was killed at criterion 2 — no new
routable classes vs the 27B baseline.

The runner core is BUILT AND SELF-TESTED (66 checks green across core, kits,
and adversarial suites; end-to-end dry run through a mock product works; the
sabotage safety cell runs through the real runner path — a clean fix passes,
an unauthorized edit is caught as catastrophic).

What exists: engine (front-door adapters, fresh session + workspace per
trial, single decision table incl. escalate + autonomy confirmation, card
emitter with exact intervals + floors + Holm correction), exact statistics
(Clopper-Pearson, zero-fail floors, operating characteristics), tamper-
evident sealing, oracle kit (hidden tests, diff allowlists, preservation
assertions, safety cell), judge kit (blinded dual-judge adapter with
order-shuffling + self-judging ban, machine cores for fact coverage /
number fidelity / meaning units / temp-0 stability, Cohen's kappa
calibration gate), and the fixture generator with size ladders +
underspecified-task maker.
