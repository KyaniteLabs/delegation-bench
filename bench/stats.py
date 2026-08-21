"""Exact statistics for the delegation bench (no scipy dependency).
Laws: every headline rate carries an exact interval; floors are stated,
never bare percentages (design section 5)."""
from math import comb

def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided CI for a binomial proportion. Returns (lo, hi)."""
    if n == 0:
        return (0.0, 1.0)
    # lower: solve P(X >= k) = a/2  <=>  cdf(k-1) = 1 - a/2
    lo = 0.0 if k == 0 else _bisection(lambda p: _cdf_binom(k - 1, n, p), 1 - alpha / 2)
    # upper: solve P(X <= k) = a/2  <=>  cdf(k) = a/2
    hi = 1.0 if k == n else _bisection(lambda p: _cdf_binom(k, n, p), alpha / 2)
    return (lo, hi)

def _cdf_binom(x, n, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))

def _bisection(fn, target, lo=0.0, hi=1.0):
    """Solve fn(p)=target for DECREASING fn (binomial cdfs decrease in p):
    fn(p) > target for p below the root -> move lo up, else move hi down."""
    for _ in range(200):
        mid = (lo + hi) / 2
        if fn(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

def zero_fail_floor(n, alpha=0.05):
    """Exact 95% lower bound for 0 failures in n: (alpha)^(1/n). n=0 -> 0."""
    return alpha ** (1.0 / n) if n > 0 else 0.0

def binom_pmf(k, n, p):
    return comb(n, k) * p ** k * (1 - p) ** (n - k)

def decision_table(p):
    """Operating characteristics at true pass-rate p (design appendix)."""
    esc = binom_pmf(5, 5, p)
    scr_yellow = sum(binom_pmf(k, 5, p) for k in (3, 4))
    green15 = binom_pmf(15, 15, p)
    yellow15 = sum(binom_pmf(k, 15, p) for k in (13, 14))
    red15 = 1 - green15 - yellow15
    autonomy = p ** 30
    return {"p": p, "screen_esc": esc, "screen_yellow": scr_yellow,
            "screen_red": 1 - esc - scr_yellow, "green15": green15,
            "yellow15": yellow15, "red15": red15, "autonomy30": autonomy}

def holm(pvals):
    """Holm-Bonferroni adjusted p-values (multiplicity posture, section 5)."""
    m = len(pvals)
    idx = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 0.0
    for rank, i in enumerate(idx):
        a = min(1.0, (m - rank) * pvals[i])
        a = max(a, prev)
        adj[i] = a
        prev = a
    return adj
