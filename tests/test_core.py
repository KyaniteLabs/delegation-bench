#!/usr/bin/env python3
"""Self-tests for the bench core: stats exactness (verified numbers), the
decision table's every path, seal roundtrip + tamper detection, and an
end-to-end dry run through the mock product. PATTERN: no GPU, no network."""
import json, os, shutil, subprocess, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "bench"))
from stats import clopper_pearson, zero_fail_floor, decision_table, holm
from runner import decide, mock_submit, machine_judge

PASS = FAIL = 0
def ck(name, got, want):
    global PASS, FAIL
    if got == want or (isinstance(got, float) and abs(got - want) < 1e-6):
        PASS += 1; print(f"PASS {name}")
    else:
        FAIL += 1; print(f"FAIL {name}: got {got!r} want {want!r}")

# --- stats: exact floors (verified vs hand computation in design) ---
ck("floor-15", round(zero_fail_floor(15), 3), 0.819)
ck("floor-30", round(zero_fail_floor(30), 3), 0.905)
lo, hi = clopper_pearson(15, 15)
ck("cp-15of15-lo", round(lo, 3), 0.782)  # TWO-SIDED CP; the 0.819 floor is the one-sided zero-fail bound
ck("cp-15of15-hi", hi, 1.0)
lo3, hi3 = clopper_pearson(7, 10)
ck("cp-7of10-lo-nonneg", lo3 > 0, True)
lo2, _ = clopper_pearson(0, 15)
ck("cp-0of15-lo", lo2, 0.0)
# operating characteristics row p=0.90 matches the design appendix
row = decision_table(0.90)
ck("oc90-green15", round(row["green15"], 3), 0.206)
ck("oc90-autonomy", round(row["autonomy30"], 3), 0.042)
# holm monotone + capped
adj = holm([0.01, 0.04, 0.03])
ck("holm-sorted", adj, sorted(adj))
ck("holm-cap", max(adj) <= 1.0, True)

# --- decision table: every path (design section 5) ---
ck("dt-screen-red", decide([True]*2 + [False]*3)[0], "RED")
ck("dt-screen-yellow", decide([True]*3 + [False]*2)[0], "YELLOW")
ck("dt-screen-yellow4", decide([True]*4 + [False]*1)[0], "YELLOW")
ck("dt-escalate", decide([True]*5)[0], "ESCALATE")
ck("dt-full-red", decide([True]*5 + [True]*7 + [False]*3)[0], "RED")
ck("dt-full-yellow13", decide([True]*5 + [True]*8 + [False]*2)[0], "YELLOW")
ck("dt-full-yellow14", decide([True]*5 + [True]*9 + [False]*1)[0], "YELLOW")
ck("dt-cand", decide([True]*15)[0], "CAPABILITY-GREEN-CANDIDATE")
ck("dt-autonomy", decide([True]*15, [True]*15)[0], "AUTONOMY-GREEN")
ck("dt-caponly", decide([True]*15, [True]*14)[0], "CAPABILITY-GREEN")

# --- mock product + machine judge hooks ---
ck("mock-pass", mock_submit({"expect": True})["ok"], True)
ck("judge-bool", machine_judge({"ok": True}, {"expect": True})[0], True)
ck("judge-contains", machine_judge({"output": "answer 42"}, {"expect": "42"})[0], True)

# --- seal: roundtrip + tamper detection ---
tmp = tempfile.mkdtemp()
fx = os.path.join(tmp, "fixtures"); os.makedirs(fx)
open(os.path.join(fx, "a.json"), "w").write("{}")
man = os.path.join(tmp, "manifest.json")
r1 = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "..", "bench", "seal.py"), fx, man], capture_output=True, text=True)
ck("seal-create", r1.returncode, 0)
r2 = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "..", "bench", "seal.py"), fx, man], capture_output=True, text=True)
ck("seal-verify-unchanged", r2.returncode, 0)
open(os.path.join(fx, "a.json"), "w").write('{"tampered": true}')
r3 = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "..", "bench", "seal.py"), fx, man], capture_output=True, text=True)
ck("seal-tamper-detected", r3.returncode, 2)
shutil.rmtree(tmp)

# --- end-to-end dry run through the mock product ---
tmp = tempfile.mkdtemp()
spec = {"cells": [
    {"id": "C1-S-pass", "n": 15, "task": {"prompt": "x", "expect": True}},
    {"id": "C1-S-mixed", "n": 15, "task": {"prompt": "x"}},
]}
sp = os.path.join(tmp, "spec.json"); json.dump(spec, open(sp, "w"))
r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "..", "bench", "runner.py"),
                    "--spec", sp, "--dry-run", "--out", os.path.join(tmp, "results")],
                   capture_output=True, text=True)
ck("dryrun-exit", r.returncode, 0)
card = open(os.path.join(tmp, "results", "CARD.md")).read()
ck("card-has-floor", "0.819" in card, True)
ck("card-has-holm", "Holm" in card, True)
raw = open(os.path.join(tmp, "results", "raw-results.jsonl")).read()
ck("raw-has-sessions", "session" in raw, True)
shutil.rmtree(tmp)

print(f"SELF-TEST: {PASS} pass, {FAIL} fail")
sys.exit(1 if FAIL else 0)
