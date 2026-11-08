# Delegation measurement architecture

```text
run spec + sealed fixture design -> fresh trial/session -> HTTP/CLI product front door
 -> response/workspace -> oracle/judge -> decision table + statistical floors -> card/raw records
```

[runner.py](bench/runner.py) selects HTTP/CLI adapters, creates per-trial workspaces and dispatches hidden tests, safety cells, fact coverage or simple expectations. `--dry-run` substitutes deterministic mock submission, not a local model. [stats.py](bench/stats.py) implements exact binomial intervals, one-sided zero-failure floors and Holm adjustment without SciPy. These are different quantities; interval assumptions do not establish test independence or real-world safety.

`oracles/` supplies hidden tests, allowlists and a sabotage fixture; `judges/` supplies machine cores, calibration/golden fixtures and the generic dual-judge scaffold. Specialized `bench/*` experiments and dated `results/` are distinct from the reusable runner. Sealing records hashes, not secret publication or semantic validity.

## Trust / failure boundaries

- Real CLI adapters execute commands; hidden-test oracles execute submitted code; run specs/endpoints/code need isolation and approval. Fresh directories are not a security sandbox. Trials and tests may create/remove scratch files, so the docs proof avoids whole-suite/workspace execution.
- Generic no-expectation judging returns `(True, 'no-check')`; this is not success at a real task. Generic non-mock judge scoring is unimplemented, and its disagreement expression does not honor a false tie-break. Do not generalize mock/self-test green into live judging quality.
- Confidence floors depend on the sampled configuration, task population and dependence assumptions. Historical “certified” cards do not certify a changed model, provider, harness or today's fleet. Do not expose sealed holdouts, personal tasks or raw traces merely to strengthen docs.

## Docs proof

Actual runner/statistics/judge source read; pure one-sided floor, interval endpoint, escalation/autonomy and no-check assertions passed; 24 Python files AST-parsed. No trials/model/network, destructive cleanup, holdout access or independent historical/real-world acceptance. Runtime unchanged; revert docs for rollback.
