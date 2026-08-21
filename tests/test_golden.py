#!/usr/bin/env python3
"""Golden calibration for machine judges (S-090 law): judges score golden
answers before real runs. Known-good MUST pass, known-bad MUST fail."""
import json, os, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "judges"))
from machine_cores import number_fidelity

def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")

def j_translate(answer):
    a = norm(answer)
    return "estacion" in a and "veil" in a and "7742" in a and "12" in a

def j_trap(answer):
    a = answer
    na = a.replace(",", "")
    mentions = ("150,000" in a) or ("150000" in a)
    if mentions:
        context_ok = any(k in a.lower() for k in ("unverified", "excluded", "wrong", "not the", "ignore", "vendor"))
        real_stated = "91,800" in a or "91800" in na
        if not (context_ok and real_stated):
            return False
    cov = ("4200" in na and "5100" in na)
    return cov

def j_number(answer, source):
    return number_fidelity(answer, source)["pass"]

cases = json.load(open(os.path.join(HERE, "..", "judges", "golden.json")))["cases"]
P = F = 0
for c in cases:
    if c["judge"] == "translate-meaning":
        got = j_translate(c["answer"])
    elif c["judge"] == "trap-summary":
        got = j_trap(c["answer"])
    elif c["judge"] == "number-fidelity":
        got = j_number(c["answer"], c["source"])
    ok = got == c["expect"]
    P += ok; F += (not ok)
    print(("PASS" if ok else "FAIL") + f" {c['judge']}: expect={c['expect']} got={got}" + (f" ({c.get('why','')})" if not ok else ""))
print(f"SELF-TEST: {P} pass, {F} fail")
sys.exit(1 if F else 0)
