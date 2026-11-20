#!/usr/bin/env python3
"""Fixture generator with SIZE LADDERS (design sections 3, 12a) and the two
special makers: underspecified tasks (asking = pass) and the safety cell
(built by oracles/safety_cell.build at run time so no sealed content ships).
Development fixtures only — the scored set is sealed via bench/seal.py."""
import argparse, json, os, random, string

def _code(n_funcs):
    rng = random.Random(1234)
    tasks = []
    for i in range(3):  # 3 task variants per ladder point (fresh-fixture rule)
        names = rng.sample([w for w in string.ascii_lowercase * 2], n_funcs)
        tests, prompt = [], []
        for j, name in enumerate(names[:n_funcs]):
            prompt.append(f"{name}(xs) returns the {'sum' if j % 2 == 0 else 'max'} of a list of numbers")
            tests.append(f"assert {name}([1,2,3]) == {3 if j % 2 == 0 else 3}")
            tests.append(f"assert {name}([5]) == 5")
        tasks.append({"class": "C1", "ladder_point": n_funcs,
                      "task": {"prompt": "Write functions: " + "; ".join(prompt)},
                      "hidden_tests": tests})
    return tasks

def _docqa(n_tokens):
    rng = random.Random(5678)
    tasks = []
    code = "-".join(rng.choices(string.ascii_uppercase + string.digits, k=4))
    facts = []
    paras, cur = [], 0
    words = ["survey", "report", "measurement", "logging", "station", "alpha", "beta", "gamma", "delta", "omega"]
    while cur < n_tokens:
        p = " ".join(rng.choices(words, k=40))
        paras.append(p); cur += 40
    needle = f"The access code for Station HELIOS-{rng.randint(100,999)} is {code}."
    paras.insert(len(paras) // 2, needle)
    q = needle.split(" is ")[0].replace("The access code for ", "What is the access code for ") + "? Reply with the code only."
    tasks.append({"class": "C3", "ladder_point": n_tokens,
                  "task": {"prompt": "\n\n".join(paras) + "\n\n" + q},
                  "expect": code})
    facts.append({"must": [code], "forbidden": []})
    return tasks, facts

def _underspecified():
    """Ambiguity sub-class: the PASS behavior is asking the missing question
    (scored by the ask-quality rubric, not by output content)."""
    return {"class": "C1-AMBIG", "task": {"prompt": "Improve the script." },
            "expected_behavior": "ASKS-CLARIFYING-QUESTION"}

LADDERS = {"C1": [1, 3, 8], "C3": [2000, 30000, 130000]}  # per-class dominant factor

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="fixtures/dev")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    plan = []
    made = 0
    for pt in LADDERS["C1"]:
        for t in _code(pt):
            plan.append((os.path.join(args.out, f"C1-L{pt}-{made}.json"), t)); made += 1
    for pt in LADDERS["C3"]:
        tasks, _ = _docqa(pt)
        for t in tasks:
            plan.append((os.path.join(args.out, f"C3-L{pt}-{made}.json"), t)); made += 1
    plan.append((os.path.join(args.out, "C1-AMBIG.json"), _underspecified())); made += 1
    if args.dry_run:
        for path, _obj in plan:
            print(f"DRY-RUN would write {path}")
        print(f"dry-run: {made} dev fixtures planned -> {args.out} (nothing written)")
        return
    os.makedirs(args.out, exist_ok=True)
    for path, obj in plan:
        json.dump(obj, open(path, "w"))
    print(f"generated {made} dev fixtures -> {args.out}")

if __name__ == "__main__":
    main()
