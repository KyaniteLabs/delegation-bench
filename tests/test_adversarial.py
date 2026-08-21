#!/usr/bin/env python3
"""Adversarial scenarios for the runner (ultraqa class): malformed inputs,
tamper detection, self-judge ban, zero-n, fake-success text."""
import json, os, subprocess, sys, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
R = []
def rec(name, ok): R.append((name, ok)); print(("PASS " if ok else "FAIL ") + name)
t = tempfile.mkdtemp()
open(f"{t}/spec.json","w").write("{not json")
rec("adv1-malformed-clean", subprocess.run([sys.executable, f"{ROOT}/bench/runner.py", "--spec", f"{t}/spec.json", "--dry-run"], capture_output=True).returncode != 0)
rec("adv2-missing-clean", subprocess.run([sys.executable, f"{ROOT}/bench/runner.py", "--spec", f"{t}/nope.json", "--dry-run"], capture_output=True).returncode != 0)
sys.path.insert(0, f"{ROOT}/judges")
from llm_judge import JudgeAdapter
try:
    JudgeAdapter({"sut_model": "m1", "judge_a_model": "m1", "judge_b_model": "m2", "tiebreak_model": "m3"}); rec("adv3-self-judge", False)
except AssertionError: rec("adv3-self-judge", True)
fx = f"{t}/fx"; os.makedirs(fx); open(f"{fx}/a.json","w").write("{}"); man = f"{t}/man.json"
subprocess.run([sys.executable, f"{ROOT}/bench/seal.py", fx, man], capture_output=True)
open(f"{fx}/a.json","w").write('{"x":1}')
rec("adv4-tamper-blocks", subprocess.run([sys.executable, f"{ROOT}/bench/seal.py", fx, man], capture_output=True).returncode == 2)
open(f"{t}/s5.json","w").write(json.dumps({"cells": [{"id": "Z", "n": 0, "task": {"expect": True}}]}))
rec("adv5-zero-n", subprocess.run([sys.executable, f"{ROOT}/bench/runner.py", "--spec", f"{t}/s5.json", "--dry-run", "--out", f"{t}/o5"], capture_output=True).returncode == 0)
sys.path.insert(0, f"{ROOT}/bench")
from runner import machine_judge
ok, _ = machine_judge({"output": "T0 PASS T1 PASS faked"}, {"hidden_tests": ["assert 1==2"]}, workspace=t)
rec("adv6-fake-pass-text-rejected", ok is False)
ok7, _ = machine_judge({"output": "no numbers"}, {"fact_spec": {"must": [], "forbidden": []}})
rec("adv7-empty-factspec", ok7 is True)
shutil.rmtree(t)
npass = sum(ok for _, ok in R)
print(f"SELF-TEST: {npass} pass, {len(R)-npass} fail")
sys.exit(0 if npass == len(R) else 1)
