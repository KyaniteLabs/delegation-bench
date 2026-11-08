# Delegation Benchmark

A research/measurement toolkit for deciding which operator jobs may be delegated to a particular model-plus-product configuration. It evaluates repeatability, asking/escalation and autonomy separately rather than treating a general capability score as permission to walk away.

## Existing artifacts

- Pre-registered nine-class/size-ladder design, research, fixture generator, sealing method, HTTP/CLI front-door runner and a single escalation/decision table.
- Exact interval/zero-failure floor calculations, multiplicity adjustment, hidden-test/diff/safety oracles, machine scoring and judge-calibration utilities.
- Historical result cards/raw logs for dated configurations. README's measured-trial totals and “certified” labels are repository claims, not newly reproduced or independently certified results here; holdouts are deliberately not public.

## Important limits

Actual generic `JudgeAdapter.score` only implements mock scoring; non-mock raises `NotImplementedError`. Its tie-adjudication expression is not the documented majority rule: disagreements become true regardless of a false tie-break. Generic `machine_judge` with no expected value/oracle returns true/`no-check`. Thus a green runner/card is not sufficient evidence of useful or safe delegation. Dated specialized runners/results require their own audit.

Pure actual statistics, escalation/autonomy and `no-check` behavior were exercised; 24 Python sources parsed. No trial workspace, cleanup, external model/product, sealed holdout, fresh experiment or historical result reproduction. No current operator/autonomy acceptance. See [ARCHITECTURE.md](ARCHITECTURE.md), [design](DESIGN.md) and [results](results/).
