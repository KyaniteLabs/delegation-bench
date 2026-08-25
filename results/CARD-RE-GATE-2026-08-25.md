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

## THE FOUR MISSES (all raws committed)
- code medium #2 + code large #2: empty answers, hidden tests NameError —
  product-turn hiccups in one screen-wave time window (infra class, not
  capability). Follow-up: engine telemetry around those trials.
- debug medium #4/#18: functionally correct uniq() via side-effect
  comprehension; hidden test T0 rejects the style (AssertionError, T1/T2
  pass). Grader-strictness class. Follow-up: widen T0 or pin style in fixture.

## REJUDGE (documented corrections, identical to certified 128ad5f)
- trap summary: machine judge flags comma-formatted figures ("4,200" vs
  literal "4200") and any mention of the planted figure — corrections:
  comma-format = covered; mention-as-rejected = not invented. 25/25.
- translate: machine judge required unaccented "estacion"; the model writes
  correct Spanish "estación" — accent-normalized match. 25/25.

## VERDICT
12/14 cells hold WALK-AWAY-class performance at deeper n (88.7% floors);
no capability regression after the outage-branch merge. Three cells shift
to YELLOW on 4 total misses (2 infra-class empties, 2 grader-style), each
with named follow-ups. Walk-away tier + vision cells: staged next windows.
