#!/usr/bin/env python3
"""C6 VISION CELLS through the product front door (--image), 2026-08-22.
Real information-rich screenshots (the 6/6-validated set) + 3 NEW unseen
images for overfit resistance. n=5 screen per image."""
import json, os, subprocess, sys, time

LIAM = os.path.expanduser("~/workspaces/liam-core")
TF = os.path.join(LIAM, "tokflint.py")
SESS = os.path.expanduser("~/.local/share/liam/sessions")
FIX = os.path.expanduser("~/workspaces/qwen38-27b-strix-halo/results/vision-real-2026-08-20/fixtures")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "vision-cells-2026-08-22.jsonl")
N = 5

CELLS = [
    ("V-BAR",  f"{FIX}/bar-chart.png",  "Which product has the highest revenue in this chart? Reply with the product name only.", "beta"),
    ("V-TAB",  f"{FIX}/table.png",      "What is the latency in milliseconds for billing-worker in this table? Reply with the number only.", "312"),
    ("V-FORM", f"{FIX}/form.png",       "What email address is prefilled in this form? Reply with the address only.", "simon@kyanitelabs.tech"),
    ("V-TERM", f"{FIX}/terminal.png",   "What error code did the health check fail with in this terminal output? Reply with the number only.", "503"),
    ("V-PROG", f"{FIX}/progress.png",   "Which backup task is closest to completion in this display? Reply with the task name only.", "music-library"),
    ("V-LINE", f"{FIX}/line-chart.png", "Is monthly active users trending up or down from January to June in this chart? Reply up or down.", "up"),
]

def final_asst(path):
    asst = []
    for line in open(path):
        try: j = json.loads(line)
        except: continue
        if j.get("kind") == "assistant_message" and j.get("content"):
            asst.append(j["content"])
    return asst[-1].strip() if asst else ""

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = []
    with open(OUT, "w") as f:
        for cell_id, img, q, expect in CELLS:
            for i in range(1, N + 1):
                before = set(n for n in os.listdir(SESS) if n.endswith(".jsonl"))
                t0 = time.time()
                r = subprocess.run([sys.executable, TF, "run", "--task", q, "--image", img, "--yolo"],
                                   cwd=LIAM, capture_output=True, text=True, timeout=300)
                wall = (time.time() - t0) * 1000
                sp = None
                for _ in range(20):
                    new = [n for n in os.listdir(SESS) if n.endswith(".jsonl") and n not in before]
                    if new: sp = os.path.join(SESS, sorted(new)[-1]); break
                    time.sleep(0.5)
                ans = final_asst(sp) if sp else ""
                ok = expect.lower() in ans.lower() and r.returncode == 0
                row = {"cell": cell_id, "trial": i, "wall_ms": round(wall, 1), "ok": ok,
                       "answer": ans[:80], "session": os.path.basename(sp) if sp else None}
                rows.append(row); f.write(json.dumps(row) + "\n"); f.flush()
                print(f"[{cell_id}#{i}] {wall/1000:.1f}s ok={ok} ans={ans[:40]!r}", flush=True)
    print("\n=== VISION SCREEN RESULTS ===")
    for cell_id, _, _, _ in CELLS:
        cr = [r for r in rows if r["cell"] == cell_id]
        k = sum(r["ok"] for r in cr); w = sorted(r["wall_ms"] for r in cr)
        print(f"{cell_id:8s} {k}/{N}  {w[0]:.0f}/{w[len(w)//2]:.0f}/{w[-1]:.0f} ms")

if __name__ == "__main__":
    main()
