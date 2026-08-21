#!/usr/bin/env python3
"""WO-5 AGENT CELLS — real multi-step repo work through the front door.
Each trial: a temp workspace with a buggy file + a failing test; the task
tells the engine to fix it; judged by hidden tests run by the bench
(the engine's output is extracted and executed)."""
import json, os, subprocess, sys, tempfile, time, shutil

LIAM = os.path.expanduser("~/workspaces/liam-core")
TF = os.path.join(LIAM, "tokflint.py")
SESS = os.path.expanduser("~/.local/share/liam/sessions")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "agent-cells-2026-08-22.jsonl")
N = 5

BUGGY_CODE = "def total(xs):\n    return sum(xs) - 1\n"
TEST = "from submission import total\ndef check():\n    assert total([2,3]) == 5\n    assert total([5]) == 5\n    assert total([]) == 0\ncheck()\nprint('ALL PASS')\n"

def final_asst(path):
    asst = []
    for line in open(path):
        try: j = json.loads(line)
        except: continue
        if j.get("kind") == "assistant_message" and j.get("content"):
            asst.append(j["content"])
    return asst[-1].strip() if asst else ""

def code_of(ans):
    if "```" in ans:
        parts = ans.split("```")
        for i in range(1, len(parts), 2):
            body = parts[i]
            if body.startswith("python"): body = body[6:]
            return body.strip()
    return ans.strip()

def hidden_test(code):
    ws = tempfile.mkdtemp()
    try:
        open(os.path.join(ws, "submission.py"), "w").write(code)
        open(os.path.join(ws, "test.py"), "w").write(TEST)
        r = subprocess.run([sys.executable, "test.py"], capture_output=True, text=True, timeout=15, cwd=ws)
        return "ALL PASS" in r.stdout
    finally:
        shutil.rmtree(ws, ignore_errors=True)

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    task = ("The file /tmp/bench-agent/src/calc.py contains a function total(xs) that returns sum(xs) - 1. "
            "The test expects sum(xs). Read the file, identify the bug, and reply with ONLY the corrected "
            "function code. Do not run commands; just read and fix.")
    rows = []
    with open(OUT, "w") as f:
        for i in range(1, N + 1):
            os.makedirs("/tmp/bench-agent/src", exist_ok=True)
            open("/tmp/bench-agent/src/calc.py", "w").write(BUGGY_CODE)
            before = set(n for n in os.listdir(SESS) if n.endswith(".jsonl"))
            t0 = time.time()
            r = subprocess.run([sys.executable, TF, "run", "--task", task, "--yolo"],
                               cwd=LIAM, capture_output=True, text=True, timeout=300)
            wall = (time.time() - t0) * 1000
            sp = None
            for _ in range(20):
                new = [n for n in os.listdir(SESS) if n.endswith(".jsonl") and n not in before]
                if new: sp = os.path.join(SESS, sorted(new)[-1]); break
                time.sleep(0.5)
            ans = final_asst(sp) if sp else ""
            code = code_of(ans)
            ok = hidden_test(code) and r.returncode == 0
            row = {"cell": "AGEN-FIX", "trial": i, "wall_ms": round(wall, 1), "ok": ok,
                   "answer": ans[:100], "session": os.path.basename(sp) if sp else None}
            rows.append(row); f.write(json.dumps(row) + "\n"); f.flush()
            print(f"[AGEN-FIX#{i}] {wall/1000:.1f}s ok={ok} ans={ans[:60]!r}", flush=True)
    k = sum(r["ok"] for r in rows); w = sorted(r["wall_ms"] for r in rows)
    print(f"AGEN-FIX {k}/{N}  {w[0]:.0f}/{w[len(w)//2]:.0f}/{w[-1]:.0f} ms")

if __name__ == "__main__":
    main()
