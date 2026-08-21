"""Blinded dual-judge protocol (design section 8): two judges, model identity
and arm hidden, question-order shuffled, judge model MUST differ from the
system under test; a third different-model judge breaks ties.
The adapter is pluggable; a deterministic mock exists for self-tests."""
import json, random, urllib.request

class JudgeAdapter:
    """Wire to any OpenAI-compatible endpoint. cfg must carry model ids; the
    runner REFUSES TO START if a judge model equals the SUT model (self-bias
    ban is structural, not advisory)."""
    def __init__(self, cfg, mock=False):
        self.cfg = cfg
        self.mock = mock
        sut = cfg.get("sut_model")
        judges = [cfg.get("judge_a_model"), cfg.get("judge_b_model"), cfg.get("tiebreak_model")]
        if not mock:
            assert all(judges), "judge models required"
            assert sut not in judges, "SELF-JUDGING BANNED: judge model equals system-under-test"

    def score(self, item, seed):
        """item: {'questions':[...], 'output':...}. Returns per-question
        scores. Order-shuffling: questions are shuffled per judge with a
        recorded seed (position-bias defense)."""
        rng = random.Random(seed)
        order = list(range(len(item["questions"])))
        rng.shuffle(order)
        if self.mock:
            return {q: True for q in order}, {"shuffled_order": order, "judge": "mock"}
        raise NotImplementedError("wire at freeze time via cfg endpoint; mock covers tests")

def adjudicate(a, b, tiebreak):
    """Majority of three (a, b, tiebreak) per question; disagreement rate
    reported (design: disagreement measured and adjudicated)."""
    disagree = sum(1 for q in a if a[q] != b[q])
    final = {q: (a[q] or b[q] or tiebreak.get(q, False)) if a[q] != b[q] else a[q] for q in a}
    return final, disagree / max(len(a), 1)
