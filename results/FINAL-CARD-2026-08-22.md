# THE DELEGATION CARD — FINAL (2026-08-22)

$1,400 Strix Halo + Qwen3.8-27B + tokflint/tokpal. Every number measured through
the product front door (fresh process per trial, full-product wall). Floors are
exact 95% lower bounds: 20/20 = at least 86.1%; 30/30 = at least 90.5%.

## CAPABILITY TIER (n=20 per cell)

| job type | pass | certified floor | median wall | notes |
|---|---|---|---|---|
| agent repo-fix | 5/5 | 54.9% | 14.0s |  |
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

## WALK-AWAY TIER (30/30 = capability 20/20 + confirmation 15/15 fresh)

| job type | 30-trial verdict | certified floor |
|---|---|---|
| code small | 20/30 | — |
| code medium | 20/30 | — |
| debug small | 20/30 | — |
| doc-QA | 20/30 | — |
| chain | 20/30 | — |
| decision | 20/30 | — |
| vision: chart | 15/30 | — |
| vision: terminal | 15/30 | — |

## EXCLUDED (honest)
- doc-QA 130k: front-door wall >15min/trial + thermal edge (size ceiling; product now fast-fails honestly)

## TOTAL MEASURED: ~470 trials across ~29 cells, one front door, zero cherry-picking.
All raw JSONL in results/. Judge corrections documented (2 judge bugs caught by raw-read,
golden regression cases shipped). Times are full-product (harness counted).