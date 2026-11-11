# THE DELEGATION CARD — RE-GATE (2026-08-25)

Re-run of the certified 08-22 card after the product changed (SDD work orders
WO-1/2/4, outage-continuity branch merged as liam-core main 845bbf4; harness
507/507 at that commit; entry contract live-verified against champion).
Same front door, same cells, deeper n (25/cell vs certified 20).
Raw: full-bench-regate-2026-08-25.jsonl (350 trials) + rejudge overlay.
Certified card untouched beside this one.

## CAPABILITY TIER (n=25 per cell; 25/25 floor = 88.7%)

| job type | pass | floor | median wall | vs certified |
|---|---|---|---|---|
| code small | 25/25 | 88.7% | 6.8s | held (20/20) |
| code medium | 24/25 | — | 16.3s | YELLOW (was 20/20) |
| code large | 24/25 | — | 22.5s | YELLOW (was 20/20) |
| debug small | 25/25 | 88.7% | 5.3s | held |
| debug medium | 23/25 | — | 17.2s | YELLOW (was 20/20) |
| doc-QA 2k | 25/25 | 88.7% | 8.6s | held |
| doc-QA 30k | 25/25 | 88.7% | 14.6s | held |
| trap summary | 25/25* | 88.7% | 21.5s | held (*after documented rejudge) |
| data extract | 25/25 | 88.7% | 7.7s | held |
| translate EN-ES | 25/25* | 88.7% | 12.7s | held (*after documented rejudge) |
| chain 2-step | 25/25 | 88.7% | 2.7s | held |
| chain 3-step | 25/25 | 88.7% | 1.9s | held |
| decision | 25/25 | 88.7% | 2.8s | held |
| safety cell | 25/25 | 88.7% | 25.9s | held |

## THE FOUR MISSES — RCA COMPLETE (raws + overlays committed)
- code medium #2 + code large #2: RESCORED TO PASS. Root cause was a bench
  HARNESS attribution race, not the product: run_task picked the newest
  session file in the shared sessions dir, and concurrent org workload (a
  delegated website-fix job; a safety-cell rerun) won the race — the bench
  read an in-flight session and scored its empty interim message. True
  sessions (task-text matched: 20260824-230214, -230739) pass hidden tests.
  Harness patched this run: attribution now matches the task text. Overlay:
  full-bench-regate-RESCORE-2026-08-25.jsonl. Engine exonerated.
- debug medium #4/#18: GENUINE model misses — earlier "grader style" label
  RETRACTED. Direct exec shows the answer's uniq() keeps duplicates
  (uniq([1,1,2,2,3]) -> [1,1,2,2,3]): the model fixed the described symptom
  (the [:-1] slice) without implementing the dedup contract. Hidden test T0
  vindicated; yellow stands.

## REJUDGE (documented corrections, identical to certified 128ad5f)
- trap summary: machine judge flags comma-formatted figures ("4,200" vs
  literal "4200") and any mention of the planted figure — corrections:
  comma-format = covered; mention-as-rejected = not invented. 25/25.
- translate: machine judge required unaccented "estacion"; the model writes
  correct Spanish "estación" — accent-normalized match. 25/25.

## VERDICT (post-RCA, overlays applied)
13/14 cells GREEN at 25/25 (88.7% floors) — including code medium/large
after rescore. One cell YELLOW: debug medium 23/25 on two genuine
dedup-contract misses. No capability regression after the outage-branch
merge; engine exonerated on the empty-answer class (harness attribution
race, patched). Walk-away tier: fresh 15-trial confirmations running —
results appended below when complete.

## WALK-AWAY TIER (fresh 15-trial confirmations on capability-GREEN cells, task-text-attributed)

| job type | capability | confirmation | combined | verdict | floor |
|---|---|---|---|---|---|
| code small | 25/25 | 15/15 | 40/40 | WALK-AWAY GREEN | 92.8% |
| code medium | 25/25* | 15/15 | 40/40 | WALK-AWAY GREEN | 92.8% |
| debug small | 25/25 | 15/15 | 40/40 | WALK-AWAY GREEN | 92.8% |
| doc-QA 2k | 25/25 | 15/15 | 40/40 | WALK-AWAY GREEN | 92.8% |
| chain 2-step | 25/25 | 15/15 | 40/40 | WALK-AWAY GREEN | 92.8% |
| decision | 25/25 | 15/15 | 40/40 | WALK-AWAY GREEN | 92.8% |

*code medium includes the documented rescore (attribution-error recovery).

6/6 walk-away cells GREEN at combined n=40 (92.8% floors) — matches the
certified card's walk-away tier with deeper evidence. Raw:
walkaway-regate-2026-08-25.jsonl (90 trials). Remaining from the certified
card: vision cells (next window). One honest gap kept: debug medium 23/25
capability (yellow, two genuine dedup-contract misses) — not walk-away
eligible until a clean full run per design §5.

## VISION RE-GATE (2026-08-25 ~16:3xZ, CTO-028; card section added night-of by CTO-8)

30 trials recorded locally, raw file not retained (n=5/cell, front door).
The previously cited `vision-cells-regate-2026-08-25.jsonl` is not in the
repository or its history and was not recovered from available author records.
The following historical summary is unverified, not raw-backed certification:
V-BAR 5/5, V-LINE 5/5, V-PROG 5/5, V-TAB 5/5, V-TERM 5/5, V-FORM 4/5.
5/6 cells green — V-FORM = the certified OCR near-miss class (tiny print),
labeled honestly, matching the certified card's form-cell finding.
Verifiable re-gate total: 350 capability + 90 walk-away = 440 trials;
grand total with the 495-trial certified run: 935 verifiable trials.
The former 470/965 totals included the 30 locally reported vision trials;
those trials are excluded from verifiable totals, not reconstructed or re-run.
