"""C1/C2/C8 oracle: run hidden immutable tests against generated code.
Tests are NEVER shown to the system under test; the oracle executes them in
an isolated temp dir with the produced code importable."""
import json, os, subprocess, sys, tempfile

def run_hidden_tests(code_path, tests, timeout=30):
    """code_path: file the product wrote; tests: list of assert-source lines
    or file paths. Returns (passed, results)."""
    results = []
    with tempfile.TemporaryDirectory() as td:
        import shutil
        mod = os.path.join(td, "submission.py")
        shutil.copy(code_path, mod)
        loader = ["from submission import *"]
        body = []
        for i, t in enumerate(tests):
            src = open(t).read() if os.path.exists(t) else t
            body.append(f"try:\n    {src}\n    print('T{i} PASS')\nexcept Exception as e:\n    print(f'T{i} FAIL {{e}}')")
        harness = "\n".join(loader + body)
        hp = os.path.join(td, "harness.py")
        open(hp, "w").write(harness)
        r = subprocess.run([sys.executable, hp], capture_output=True, text=True,
                           timeout=timeout, cwd=td)
        for line in r.stdout.splitlines():
            if line.startswith("T") and (" PASS" in line or " FAIL" in line):
                results.append(line.strip())
    passed = all(" PASS" in x for x in results) and results
    return bool(passed), results

def check_test_integrity(original_tests, post_run_tests):
    """Mutation check: hidden tests must be byte-identical before/after."""
    return original_tests == post_run_tests
