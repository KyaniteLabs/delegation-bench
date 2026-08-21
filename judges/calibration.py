"""Judge calibration (design section 8): judge-vs-human agreement must pass
a pre-set threshold BEFORE the freeze. Cohen's kappa on pass/fail labels."""
def cohen_kappa(a, b):
    assert len(a) == len(b) and len(a) > 0
    labels = sorted(set(a) | set(b))
    po = sum(x == y for x, y in zip(a, b)) / len(a)
    pe = sum((a.count(l) / len(a)) * (b.count(l) / len(b)) for l in labels)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)

def calibration_gate(judge_labels, human_labels, threshold=0.6):
    k = cohen_kappa(judge_labels, human_labels)
    return {"pass": k >= threshold, "kappa": round(k, 3), "threshold": threshold}
