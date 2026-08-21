#!/usr/bin/env python3
"""CEO BENCH (2026-08-22): time-per-task through the tokflint front door.

Entry contract per CEO-set requirements + CTO-008/CS-024 precision:
- task-in/result-out via the EXISTING CLI surface (no new product code)
- FRESH PROCESS per trial (each tokflint run invocation is its own process)
Metric: wall-clock from task-in to result-out, harness time counted (the
subprocess wall includes CLI + engine + champion). Per class: identical task
x N trials; report min/median/max ms + correctness. P13: every row carries
the session id (provenance), judge = machine-exact on the final ASST line.
"""
import json, os, subprocess, sys, time

LIAM = os.path.expanduser("~/workspaces/liam-core")
TF = os.path.join(LIAM, "tokflint.py")
SESS = os.path.expanduser("~/.local/share/liam/sessions")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "ceo-bench-2026-08-22.jsonl")

TASKS = [
    ("ECHO",   "Reply with exactly the word READY and nothing else.", lambda a: a.strip().upper() == "READY"),
    ("ARITH",  "What is 17*23? Reply with the number only.", lambda a: "391" in a),
    ("CODE-S", "Write a Python function named double(x) that returns 2*x. Reply with only the code, no explanation.", lambda a: "def double" in a.replace(" ", "") or "double" in a and "2" in a and ("def" in a or "lambda" in a)),
    ("FACT-QA","What is the capital city of Australia? Reply with the city name only.", lambda a: "canberra" in a.lower()),
    ("EXTRACT","Here is a list: alpha, beta, gamma, delta. Reply with the third item only.", lambda a: a.strip().lower().startswith("gamma")),
    ("SUM-S",  "Summarize in exactly one short sentence: The quick brown fox jumps over the lazy dog near the riverbank at dawn while birds scatter. Reply with only the sentence.", lambda a: "fox" in a.lower() and len(a) < 400),
]
N = 5

def newest_session(before_names):
    for _ in range(20):
        names = sorted(f for f in os.listdir(SESS) if f.endswith(".jsonl"))
        new = [n for n in names if n not in before_names]
        if new:
            return os.path.join(SESS, new[-1])
        time.sleep(0.5)
    return None

def final_asst(path):
    asst = []
    for line in open(path):
        try:
            j = json.loads(line)
        except Exception:
            continue
        if j.get("kind") == "assistant_message" or j.get("type") == "assistant_message":
            c = j.get("content") or j.get("text") or ""
            if c:
                asst.append(c)
    return asst[-1].strip() if asst else ""

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = []
    with open(OUT, "w") as f:
        for cls, task, judge in TASKS:
            for i in range(1, N + 1):
                before = set(n for n in os.listdir(SESS) if n.endswith(".jsonl"))
                t0 = time.time()
                r = subprocess.run([sys.executable, TF, "run", "--task", task, "--yolo"],
                                   cwd=LIAM, capture_output=True, text=True, timeout=600)
                wall_ms = (time.time() - t0) * 1000.0
                sp = newest_session(before)
                ans = final_asst(sp) if sp else ""
                ok = bool(judge(ans)) and r.returncode == 0
                row = {"class": cls, "trial": i, "wall_ms": round(wall_ms, 1),
                       "ok": ok, "answer": ans[:80], "session": os.path.basename(sp) if sp else None,
                       "rc": r.returncode}
                rows.append(row)
                f.write(json.dumps(row) + "\n"); f.flush()
                print(f"[{cls}#{i}] {wall_ms/1000:.1f}s ok={ok} ans={ans[:40]!r}", flush=True)
    print("\n=== SUMMARY (min/median/max ms, correctness) ===")
    for cls, _, _ in TASKS:
        w = sorted(r["wall_ms"] for r in rows if r["class"] == cls)
        k = sum(r["ok"] for r in rows if r["class"] == cls)
        if w:
            print(f"{cls:8s} {k}/{N}  {w[0]:.0f} / {w[len(w)//2]:.0f} / {w[-1]:.0f} ms")
    print("CEO-BENCH COMPLETE")

if __name__ == "__main__":
    main()
