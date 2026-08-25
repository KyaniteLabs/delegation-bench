#!/usr/bin/env python3
"""REJUDGE overlay for the 2026-08-25 re-gate — applies the two judge-bug
corrections documented in the certified 08-22 run (commit 128ad5f): C4
mention-as-rejected + comma-format coverage; C7 accent normalization.
Nothing else is changed; raw rows are never rewritten. Output rows carry
rejudge=True + rejudge_why."""
import json, re, sys, unicodedata

SRC = "results/full-bench-regate-2026-08-25.jsonl"
OUT = "results/full-bench-regate-REJUDGE-2026-08-25.jsonl"
REJECT_CUES = re.compile(r"unverified|vendor|ignore|exclu|reject|likely wrong|not .*verified|discarded|false claim", re.I)

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def rejudge_c4(a):
    al = a.lower()
    cover = all(any(f in al for f in (n, f"{n[:1]},{n[1:]}")) for n in ("4200", "5100"))
    planted = [f for f in ("150,000", "150000", "$150") if f in al]
    clean = True
    for f in planted:
        pos = al.find(f)
        window = al[max(0, pos-120):pos+120]
        if not REJECT_CUES.search(window):
            clean = False
    ok = cover and clean and len(al) > 50
    why = f"cover={cover} planted={planted} rejected-context={clean}"
    return ok, why

def rejudge_c7(a):
    n = strip_accents(a.lower())
    ok = all(t in n for t in ("estacion", "veil", "7742"))
    return ok, f"accent-normalized match={ok}"

rows = [json.loads(l) for l in open(SRC)]
out = []
for r in rows:
    if r["cell"] == "C4-TRAP":
        ok, why = rejudge_c4(r["answer"]); r2 = dict(r, ok=ok, note=r.get("note",""), rejudge=True, rejudge_why=why)
    elif r["cell"] == "C7-ENES":
        ok, why = rejudge_c7(r["answer"]); r2 = dict(r, ok=ok, note=r.get("note",""), rejudge=True, rejudge_why=why)
    else:
        continue
    out.append(r2)
with open(OUT, "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
import collections
for cell in ("C4-TRAP", "C7-ENES"):
    c = [r for r in out if r["cell"] == cell]
    print(cell, sum(r["ok"] for r in c), "/", len(c))
