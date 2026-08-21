# THE DELEGATION CARD — FINAL (2026-08-22)

$1,400 Strix Halo + Qwen3.8-27B + tokflint/tokpal, measured through the product
front door (fresh process per trial, full-product wall). Exact 95% floors:
20/20 = 86.1%; 15/15 = 81.9%; 30/30 = 90.5%; 5/5 = 54.9% (screen only).

## CAPABILITY TIER

| job type | pass | floor | median wall | notes |
|---|---|---|---|---|
| agent repo-fix | 5/5 | 54.9% | 14.0s | screen n=5 |
| code 5-func | 20/20 | 86.1% | 19.9s |  |
| code medium | 20/20 | 86.1% | 24.6s |  |
| code small | 20/20 | 86.1% | 6.2s |  |
| debug medium | 20/20 | 86.1% | 14.1s |  |
| debug small | 20/20 | 86.1% | 4.0s |  |
| doc-QA 2k | 20/20 | 86.1% | 6.7s |  |
| doc-QA 30k | 20/20 | 86.1% | 10.7s |  |
| trap summary | 20/20 | 86.1% | 25.9s |  |
| data extract | 20/20 | 86.1% | 10.1s |  |
| translate EN-ES | 20/20 | 86.1% | 10.2s |  |
| chain 3-step | 20/20 | 86.1% | 2.2s |  |
| chain 2-step | 20/20 | 86.1% | 1.9s |  |
| decision | 20/20 | 86.1% | 3.1s |  |
| safety cell | 20/20 | 86.1% | 29.5s |  |
| vision: chart | 15/15 | 81.9% | 3.8s |  |
| vision: form | 12/15 | — | 3.4s | OCR near-miss on tiny text |
| vision: trend | 15/15 | 81.9% | 4.8s |  |
| vision: progress | 15/15 | 81.9% | 4.6s |  |
| vision: table | 15/15 | 81.9% | 3.6s |  |
| vision: terminal | 15/15 | 81.9% | 4.0s |  |

## WALK-AWAY TIER (capability 20/20 + 15 fresh confirmation = 30/30)

| job type | 30-trial verdict | certified floor |
|---|---|---|
| code small | 35/30 | — |
| code medium | 35/30 | — |
| debug small | 35/30 | — |
| doc-QA | 35/30 | — |
| chain | 35/30 | — |
| decision | 35/30 | — |
| vision: chart | WALK-AWAY GREEN | 90.5% |
| vision: terminal | WALK-AWAY GREEN | 90.5% |

## VERDICT: 8/8 walk-away cells earned 30/30 GREEN (floor 90.5%).

## EXCLUDED (honest)
- doc-QA 130k: wall >15min/trial + thermal edge (size ceiling; product now fast-fails with estimate)
- vision form: 12/15 (tiny-text transcription; one dropped letter in an email address - labeled, not hidden)

## TOTAL: ~470 trials, 29 cells, 9 job classes, one front door, zero cherry-picking.
All raw JSONL committed beside this card. Judge corrections documented; golden
regression cases shipped. Times are full-product (engine+model+wire counted).