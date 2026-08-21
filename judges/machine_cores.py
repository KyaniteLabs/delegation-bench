"""Machine cores for C4/C7/C9 (design section 8): fact coverage, number
fidelity, meaning units. Pre-registered from SOURCE documents, never derived
from model outputs (authorship law)."""
import re

def fact_coverage(output, required_facts):
    """required_facts: list of strings that MUST appear (case-insensitive)
    plus 'forbidden': strings that must NOT (planted-contradiction traps:
    a faithful summary must surface the contradiction, not repeat it as fact)."""
    out = output.lower()
    missing = [f for f in required_facts.get("must", []) if f.lower() not in out]
    invented = [f for f in required_facts.get("forbidden", []) if f.lower() in out]
    return {"pass": not missing and not invented, "missing": missing, "invented": invented}

def number_fidelity(output, source):
    """Every number in the output must exist in the source (hallucination
    guard). Numbers normalized (commas stripped)."""
    def nums(t):
        return set(re.findall(r"\d+(?:\.\d+)?", t.replace(",", "")))
    src = nums(source)
    out = nums(output)
    invented = sorted(out - src)
    return {"pass": not invented, "invented": invented}

def meaning_units(output, units):
    """C7 core: each meaning unit (atomic fact/phrase pair) must be rendered.
    units: list of (key strings acceptable as evidence for the unit)."""
    out = output.lower()
    missing = []
    for i, alts in enumerate(units):
        if not any(a.lower() in out for a in alts):
            missing.append(i)
    return {"pass": not missing, "missing_units": missing}

def recommendation_stability(run_a, run_b):
    """C9: temp-0 stability — same inputs asked twice must yield the same
    recommendation call."""
    a = re.sub(r"\s+", " ", str(run_a)).strip().lower()
    b = re.sub(r"\s+", " ", str(run_b)).strip().lower()
    return {"pass": a == b, "stable": a == b}
