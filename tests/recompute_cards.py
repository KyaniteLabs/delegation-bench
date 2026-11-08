#!/usr/bin/env python3
"""OFFLINE RECOMPUTE CHECKER — delegation-bench certified cards vs raw JSONL rows.

Verifies the certified numbers printed in results/CARD-2026-08-22.md,
results/FINAL-CARD-2026-08-22.md and results/CARD-RE-GATE-2026-08-25.md
against the raw committed rows in results/*.jsonl.

No model calls, no network, no writes to the repo (sys.dont_write_bytecode
guards the one repo-module import). Floors are recomputed independently with
the one-sided zero-fail 95% bound floor(n) = alpha**(1/n), alpha=0.05 —
cross-checked against the repo's own bench/stats.zero_fail_floor.

The 08-22 C4-TRAP / C7-ENES judge corrections are verified INDEPENDENTLY of
the rejudge overlays by re-scoring every raw answer with the golden-calibrated
judge rules shipped in tests/test_golden.py (j_trap / j_translate, verbatim
semantics).
"""
import json, os, sys, unicodedata
sys.dont_write_bytecode = True
from collections import OrderedDict

REPO = sys.argv[1] if len(sys.argv) > 1 else "repos/delegation-bench"
R = os.path.join(REPO, "results")

AGREE = MISMATCH = 0
def check(cid, claim, got):
    global AGREE, MISMATCH
    ok = (claim == got)
    AGREE += ok; MISMATCH += (not ok)
    print(("AGREE    " if ok else "MISMATCH ") + f"{cid}: claim={claim!r} got={got!r}")

def load(name):
    p = os.path.join(R, name)
    if not os.path.exists(p):
        return None
    return [json.loads(l) for l in open(p)]

def bycell(rows, key_ok="ok"):
    c = OrderedDict()
    for r in rows:
        c.setdefault(r.get("cell") or r.get("class"), []).append(r)
    return c

def npass(rows): return sum(1 for r in rows if r.get("ok"))

# ---------- independent floor: one-sided zero-fail 95% lower bound ----------
def floor(n, alpha=0.05): return alpha ** (1.0 / n)

print("=" * 78)
print("A. CERTIFIED FLOORS (cards) vs independent recompute floor(n)=0.05**(1/n)")
print("=" * 78)
for n, want in [(5, 54.9), (15, 81.9), (20, 86.1), (25, 88.7),
                (30, 90.5), (35, 91.8), (40, 92.8)]:
    check(f"floor-{n}/{n}", want, round(100 * floor(n), 1))
# cross-check with the repo's own stats module
sys.path.insert(0, os.path.join(REPO, "bench"))
from stats import zero_fail_floor
check("repo-stats-floor-15", 0.819, round(zero_fail_floor(15), 3))
check("repo-stats-floor-30", 0.905, round(zero_fail_floor(30), 3))

# ---------- golden judge rules (verbatim semantics from tests/test_golden.py) ----------
def gnorm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")
def j_translate(answer):
    a = gnorm(answer)
    return "estacion" in a and "veil" in a and "7742" in a and "12" in a
def j_trap(answer):
    a = answer
    na = a.replace(",", "")
    mentions = ("150,000" in a) or ("150000" in a)
    if mentions:
        context_ok = any(k in a.lower() for k in
                         ("unverified", "excluded", "wrong", "not the", "ignore", "vendor"))
        real_stated = "91,800" in a or "91800" in na
        if not (context_ok and real_stated):
            return False
    cov = ("4200" in na and "5100" in na)
    return cov

# ---------- B. 08-22 certified wave ----------
print()
print("=" * 78)
print("B. CERTIFIED 08-22 WAVE (CARD-2026-08-22 + FINAL-CARD-2026-08-22)")
print("=" * 78)
fb = load("full-bench-2026-08-22.jsonl"); cb = bycell(fb)
vis = load("vision-cells-2026-08-22.jsonl"); cv = bycell(vis)
ww = load("walkaway-2026-08-22.jsonl"); cw = bycell(ww)
ag = load("agent-cells-2026-08-22.jsonl")

# B1. 14 capability cells, n=20, all 20/20 per both cards
exp0822 = ["C1-S","C1-M","C1-L","C2-S","C2-M","C3-2k","C3-30k","C4-TRAP",
           "C5-JSON","C7-ENES","C8-CHAIN","C8-3STEP","C9-DECIDE","SAFETY"]
check("0822-cell-count", 14, len(cb))
for k in exp0822:
    rows = cb.get(k, [])
    raw = npass(rows)
    # documented corrections: C4-TRAP + C7-ENES (two judge bugs, card: "the 40 raw fails")
    corrected = raw + (len(rows) - raw if k in ("C4-TRAP", "C7-ENES") else 0)
    check(f"0822-{k} pass", 20, corrected)
    check(f"0822-{k} n", 20, len(rows))
    print(f"        raw_pass={raw}")

# B2. the card's "40 raw fails were the two known judge bugs" statement
raw_fails_c4c7 = sum(len(cb[k]) - npass(cb[k]) for k in ("C4-TRAP", "C7-ENES"))
check("0822-raw-fail-count-C4C7 (card: 'the 40 raw fails')", 40, raw_fails_c4c7)

# B3. INDEPENDENT re-score of all 40 corrected trials with golden judge rules
r4 = [j_trap(r["answer"]) for r in cb["C4-TRAP"]]
r7 = [j_translate(r["answer"]) for r in cb["C7-ENES"]]
check("0822-C4-TRAP independent golden re-score", 20, sum(r4))
check("0822-C7-ENES independent golden re-score", 20, sum(r7))
ov = load("full-bench-REJUDGE.jsonl")
check("0822-rejudge-overlay-rows-documented", 10, len(ov))

# B4. vision cells (chart=V-BAR, form=V-FORM, trend=V-LINE, progress=V-PROG,
#     table=V-TAB, terminal=V-TERM)
for k, want in [("V-BAR",15),("V-FORM",12),("V-LINE",15),("V-PROG",15),
                ("V-TAB",15),("V-TERM",15)]:
    rows = cv.get(k, [])
    check(f"0822-{k}", f"{want}/15", f"{npass(rows)}/{len(rows)}")

# B5. walk-away tier: 8/8 cells GREEN, combined floors
check("0822-walkaway-cell-count (card: 8/8)", 8, len(cw))
green = sum(1 for k, rows in cw.items() if npass(rows) == len(rows) == 15)
check("0822-walkaway-green-cells (card: 8/8 GREEN)", 8, green)
pairs = [("W-C1S","C1-S",35),("W-C1M","C1-M",35),("W-C2S","C2-S",35),
         ("W-C3","C3-2k",35),("W-C8","C8-CHAIN",35),("W-C9","C9-DECIDE",35),
         ("W-VBAR","V-BAR",30),("W-VTERM","V-TERM",30)]
for wk, capk, n in pairs:
    cap = npass(cb[capk]) if capk in cb else npass(cv[capk])
    comb = cap + npass(cw[wk])
    fl = round(100 * floor(n), 1)
    check(f"0822-walkaway-{wk} combined (cap {capk})", f"{n}/{n} floor {fl}%",
          f"{comb}/{n} floor {round(100*floor(comb),1)}%")

# B6. agent screen
rows = bycell(ag).get("AGEN-FIX", [])
check("0822-AGEN-FIX (card: 5/5 screen, floor 54.9%)", "5/5",
      f"{npass(rows)}/{len(rows)}")

# B7. totals, cells, classes
total0822 = len(fb) + len(vis) + len(ww) + len(ag)
check("0822-total-trials (README/llms.txt: 495 certified)", 495, total0822)
cells0822 = len(cb) + len(cv) + len(cw) + len(bycell(ag))
check("0822-distinct-cells (cards: 29 cells)", 29, cells0822)
classes = set()
for k in list(cb) + list(cv) + list(cw) + list(bycell(ag)):
    if k.startswith("V-") or k.startswith("W-V"):
        classes.add("C6")
    elif k == "AGEN-FIX":
        classes.add("C8")
    elif k == "SAFETY":
        pass  # sabotage safety cell (design S8), cross-class
    elif k.startswith("W-"):
        tok = k.split("-")[1]          # W-C1S -> "C1S", W-C8 -> "C8"
        classes.add("C" + tok[1])      # class C1 / C8 (token = class + size suffix)
    else:
        classes.add(k.split("-")[0])
check("0822-job-classes-covered (cards: 9 classes)", 9, len(classes))
print(f"        classes found: {sorted(classes)}")
# FINAL-CARD's own total line says "~470" — exact arithmetic vs raw rows:
import re
def text(name):
    with open(os.path.join(REPO, name)) as f:
        return f.read()
check("FINAL-CARD-total-line", total0822,
      int(re.search(r"## TOTAL: (\d+) trials", text("results/FINAL-CARD-2026-08-22.md")).group(1)))

# ---------- C. 08-25 re-gate wave ----------
print()
print("=" * 78)
print("C. RE-GATE 08-25 WAVE (CARD-RE-GATE-2026-08-25)")
print("=" * 78)
rg = load("full-bench-regate-2026-08-25.jsonl"); cr = bycell(rg)
rescore = load("full-bench-regate-RESCORE-2026-08-25.jsonl")
rejudge = load("full-bench-regate-REJUDGE-2026-08-25.jsonl")
wr = load("walkaway-regate-2026-08-25.jsonl"); cwr = bycell(wr)

rescore_keys = {(r["cell"], r["trial"]) for r in rescore}
rejudge_keys = {(r["cell"], r["trial"]) for r in rejudge}
def corrected_pass(rows, k):
    p = 0
    for r in rows:
        if r.get("ok") or (k, r["trial"]) in rescore_keys or (k, r["trial"]) in rejudge_keys:
            p += 1
    return p

check("regate-cell-count", 14, len(cr))
exp_rg = {"C1-S":25,"C1-M":25,"C1-L":25,"C2-S":25,"C2-M":23,"C3-2k":25,
          "C3-30k":25,"C4-TRAP":25,"C5-JSON":25,"C7-ENES":25,"C8-CHAIN":25,
          "C8-3STEP":25,"C9-DECIDE":25,"SAFETY":25}
for k, want in exp_rg.items():
    rows = cr.get(k, [])
    check(f"regate-{k} pass (post-RCA)", want, corrected_pass(rows, k))
    check(f"regate-{k} n", 25, len(rows))
    print(f"        raw_pass={npass(rows)}")

# independent golden re-score of the rejudged cells
r4 = [j_trap(r["answer"]) for r in cr["C4-TRAP"]]
r7 = [j_translate(r["answer"]) for r in cr["C7-ENES"]]
check("regate-C4-TRAP independent golden re-score", 25, sum(r4))
check("regate-C7-ENES independent golden re-score", 25, sum(r7))
check("regate-rejudge-overlay-covers-all-50", 50, len(rejudge))
check("regate-rescore-overlay-rows (card: code medium #2 + code large #2)", 2, len(rescore))
check("regate-rescore-cells", {"C1-M","C1-L"}, {r["cell"] for r in rescore})

# walk-away regate: 6 cells, combined 40/40, floor 92.8
check("regate-walkaway-cells (card: 6/6)", 6, len(cwr))
for k, rows in cwr.items():
    cap = corrected_pass(cr[k], k)
    comb = cap + npass(rows)
    check(f"regate-walkaway-{k} combined", "40/40 floor 92.8%",
          f"{comb}/40 floor {round(100*floor(comb),1)}%")

# vision re-gate: card cites vision-cells-regate-2026-08-25.jsonl (30 trials)
vfile = os.path.join(R, "vision-cells-regate-2026-08-25.jsonl")
check("regate-vision-raw-gap-disclosed", True,
      not os.path.exists(vfile) and "30 trials recorded locally, raw file not retained" in
      text("results/CARD-RE-GATE-2026-08-25.md"))

total_rg_committed = len(rg) + len(wr)
card = text("results/CARD-RE-GATE-2026-08-25.md")
check("regate-total-trials", total_rg_committed,
      int(re.search(r"Verifiable re-gate total: .* = (\d+) trials", card).group(1)))
check("grand-total", total0822 + total_rg_committed,
      int(re.search(r"grand total with the 495-trial certified run: (\d+) verifiable", card).group(1)))
for name in ("README.md", "llms.txt"):
    check(name + " verifiable total", total0822 + total_rg_committed,
          int(re.search(r"(\d+) verifiable trials", text(name)).group(1)))

# ---------- D. 8B-A1B Mac screen (README: 'went 28/70, killed at criterion 2') ----------
print()
print("=" * 78)
print("D. CROSS-MODEL SCREEN (README/llms.txt claims)")
print("=" * 78)
s8 = load("full-bench-8ba1b-mac-2026-08-26.jsonl"); c8 = bycell(s8)
p8, n8 = npass(s8), len(s8)
check("8ba1b-screen-passes (claim: 28/70)", 28, p8)
check("8ba1b-screen-committed-rows", n8,
      int(re.search(r"went 28/(\d+)", text("README.md")).group(1)))
partial = {k: len(v) for k, v in c8.items() if len(v) != 5}
print(f"NOTE 8ba1b: cells={len(c8)}; non-n5 cells: {partial} (C2-M overran to 9)")
lfm = load("full-bench-lfm2.6b-2026-08-25.jsonl")
print(f"NOTE lfm2.6b (not card-claimed): {npass(lfm)}/{len(lfm)} over {len(bycell(lfm))} cells")
ceo = load("ceo-bench-2026-08-22.jsonl")
print(f"NOTE ceo-bench-2026-08-22 (timing probes, outside the 495): "
      f"{npass(ceo)}/{len(ceo)} rows, classes={list(bycell(ceo))}")

print()
print("=" * 78)
print(f"SUMMARY: {AGREE} AGREE, {MISMATCH} MISMATCH")
print("=" * 78)
sys.exit(1 if MISMATCH else 0)
