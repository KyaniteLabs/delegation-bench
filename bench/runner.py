#!/usr/bin/env python3
"""DELEGATION BENCH RUNNER (stage two core). Pre-registered per DESIGN.md v3.1.

Executes a run spec through the PRODUCT FRONT DOOR (adapters below), enforces
fresh session + workspace per trial, applies the single decision table
(screen n=5 -> full n=15 -> confirmation -> autonomy), and emits the card
with exact floors. Everything runs in --dry-run against a mock product.

Usage: runner.py --spec runs/spec.json [--dry-run] [--out results/]
Spec: {"cells":[{"id","class","ladder_point","n","clustered","adapter",
"workspace_template","task","judge"}]}
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time, urllib.request
from stats import clopper_pearson, zero_fail_floor, holm

# --- product entry contract adapters (the readiness gate picks one) ---
def submit_http(task, session, workspace, cfg, dry):
    if dry:
        return mock_submit(task)
    body = {"task": task, "session": session, "workspace": workspace}
    req = urllib.request.Request(cfg["url"], data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=cfg.get("timeout", 3600)) as r:
        return json.load(r)["result"]

def submit_cli(task, session, workspace, cfg, dry):
    if dry:
        return mock_submit(task)
    out = subprocess.run(cfg["cmd"], input=json.dumps({"task": task, "session": session,
        "workspace": workspace}), capture_output=True, text=True, timeout=cfg.get("timeout", 3600))
    return json.loads(out.stdout)["result"]

def mock_submit(task):
    """Deterministic mock product: passes unless the task says FAIL (test hooks)."""
    r = "FAIL" not in str(task.get("expect", ""))
    return {"ok": r, "output": "mock"}

ADAPTERS = {"http": submit_http, "cli": submit_cli}

# --- workspace: fresh per trial (design section 6) ---
def fresh_workspace(template, trial_id):
    ws = tempfile.mkdtemp(prefix=f"bench-{trial_id}-")
    if template and os.path.isdir(template):
        for item in os.listdir(template):
            shutil.copytree(os.path.join(template, item), os.path.join(ws, item), dirs_exist_ok=True)
    return ws

# --- oracles: C1/C2/C8-style machine check (full oracle kit in oracles/) ---
def machine_judge(result, task):
    expect = task.get("expect")
    if expect is None:
        return True, "no-check"
    if isinstance(expect, bool):
        return (result.get("ok") == expect), "bool"
    return (str(expect) in str(result.get("output", ""))), "contains"

# --- the single decision table (pre-registered; design section 5) ---
def decide(trial_passes, confirmation_passes=None):
    """trial_passes: list of bool (screen then full merged, in order)."""
    n5 = trial_passes[:5]
    if sum(n5) <= 2:
        return "RED", "screen <=2/5"
    if sum(n5) in (3, 4) and len(trial_passes) == 5:
        return "YELLOW", "screen 3-4/5 (confirmation pending)"
    if sum(n5) == 5 and len(trial_passes) == 5:
        return "ESCALATE", "screen 5/5 - escalate to n=15"
    n15 = trial_passes[:15]
    if len(n15) < 15:
        return "INCOMPLETE", f"{len(n15)}/15 trials"
    p15 = sum(n15)
    if p15 <= 12:
        return "RED", f"{p15}/15"
    if p15 in (13, 14):
        return "YELLOW", f"{p15}/15"
    # 15/15: capability-green candidate; autonomy needs a clean confirmation 15
    if confirmation_passes is None:
        return "CAPABILITY-GREEN-CANDIDATE", "15/15; confirmation run required"
    if sum(confirmation_passes) == 15:
        return "AUTONOMY-GREEN", "30/30"
    return "CAPABILITY-GREEN", f"15/15 first run; confirmation {sum(confirmation_passes)}/15 (autonomy not earned)"

def run_cell(cell, dry):
    results = []
    for i in range(cell["n"]):
        trial_id = f"{cell['id']}#{i+1}"
        session = hashlib.sha256(trial_id.encode()).hexdigest()[:12]
        ws = fresh_workspace(cell.get("workspace_template"), trial_id)
        t0 = time.time()
        result = ADAPTERS[cell.get("adapter", "http")](cell["task"], session, ws, cell.get("adapter_cfg", {}), dry)
        wall = time.time() - t0
        ok, how = machine_judge(result, cell["task"])
        results.append({"trial": trial_id, "session": session, "workspace": ws,
                        "ok": ok, "wall": wall, "judge": how})
        shutil.rmtree(ws, ignore_errors=True)
    return results

def emit_card(all_cells, out_path):
    lines = ["# DELEGATION CARD", "",
             "Every rate carries its exact interval; floors stated, never bare percentages.", ""]
    pvals = []
    rows = []
    for c in all_cells:
        n = len(c["results"])
        k = sum(r["ok"] for r in c["results"])
        lo, hi = clopper_pearson(k, n)
        verdict, why = c["verdict"]
        wall_med = sorted(r["wall"] for r in c["results"])[n // 2] if n else 0
        pvals.append(1 - lo)
        rows.append((c["id"], k, n, lo, hi, verdict, why, wall_med))
    adj = holm(pvals)
    lines.append("| cell | pass | exact 95% CI | floor* | verdict | why | median wall (s) | Holm-adj |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for (cid, k, n, lo, hi, v, why, wm), a in zip(rows, adj):
        floor = zero_fail_floor(n) if k == n else lo
        lines.append(f"| {cid} | {k}/{n} | [{lo:.3f}, {hi:.3f}] | >= {floor:.3f} | {v} | {why} | {wm:.1f} | {a:.3f} |")
    lines += ["", f"*floor for perfect runs = (0.05)^(1/n); 15/15 = {zero_fail_floor(15):.3f}, 30/30 = {zero_fail_floor(30):.3f}",
              "", "Failure attribution (model-limit vs routing/harness vs fixture-ambiguity) rides the raw results file."]
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    spec = json.load(open(args.spec))
    os.makedirs(args.out, exist_ok=True)
    all_cells = []
    raw_path = os.path.join(args.out, "raw-results.jsonl")
    with open(raw_path, "w") as raw:
        for cell in spec["cells"]:
            results = run_cell(cell, args.dry_run)
            verdict = decide([r["ok"] for r in results])
            cell_out = {"id": cell["id"], "results": results, "verdict": verdict}
            all_cells.append(cell_out)
            raw.write(json.dumps(cell_out) + "\n")
            print(f"[cell {cell['id']}] {verdict[0]} ({verdict[1]})", flush=True)
    emit_card(all_cells, os.path.join(args.out, "CARD.md"))
    print(f"CARD -> {args.out}/CARD.md")
    print("RUN COMPLETE")

if __name__ == "__main__":
    main()
