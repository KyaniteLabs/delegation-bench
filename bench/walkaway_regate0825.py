#!/usr/bin/env python3
"""WALK-AWAY tier for the 2026-08-25 re-gate: fresh confirmation trials
(n=15) on the capability-GREEN cells, per design v3.1 autonomy rule.
Combined verdict = 25 capability + 15 confirmation (40/40 -> 92.8% floor).
Uses the task-text session attribution fix (concurrent-traffic safe)."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import full_bench_regate0825 as fb
from lifecycle import CellLedger

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "walkaway-regate-2026-08-25.jsonl")
CELLS = ["C1-S", "C1-M", "C2-S", "C3-2k", "C8-CHAIN", "C9-DECIDE"]
N = int(os.environ.get("WALK_N", "15"))

def main():
    cells = {cid: (j, t) for cid, j, t in fb.cells()}
    prior = [json.loads(l) for l in open(OUT)] if os.path.exists(OUT) else []
    with open(OUT, "a") as f:
        for cid in CELLS:
            judge, task = cells[cid]
            ledger = CellLedger.from_rows(prior, cid, screen_n=None)  # one continuous run
            for i in ledger.pending(N):
                r = fb.run_task(task)
                res = judge(r)
                ok, note = res if isinstance(res, tuple) else (res, "bool")
                ok = bool(ok) and r["rc"] == 0
                row = {"cell": cid, "trial": i, **r, "ok": ok, "note": str(note)}
                ledger.record(i, N)
                f.write(json.dumps(row) + "\n"); f.flush()
                print(f"[W-{cid}#{i}] {r['wall_ms']/1000:.1f}s ok={ok} ans={r['answer'][:50]!r}", flush=True)
    import collections
    okc, c = collections.Counter(), collections.Counter()
    for l in open(OUT):
        d = json.loads(l); c[d["cell"]] += 1; okc[d["cell"]] += bool(d["ok"])
    print("\n=== WALKAWAY CONFIRMATION ===")
    for cid in CELLS:
        print(f"W-{cid:8s} {okc[cid]:2d}/{c[cid]:2d}")

if __name__ == "__main__":
    main()
