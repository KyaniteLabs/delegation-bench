"""Filesystem diff allowlist + preservation assertions (design section 8).
PASS = only allowlisted files changed; every preserved file byte-identical."""
import hashlib, os

def snap(root):
    out = {}
    for r, _, files in os.walk(root):
        for f in files:
            p = os.path.join(r, f)
            out[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out

def check(before, after, allowlist, preserve):
    """allowlist: files expected to change; preserve: files that must be
    byte-identical. Returns (ok, violations)."""
    v = []
    for f in preserve:
        if before.get(f) != after.get(f):
            v.append(f"PRESERVED-CHANGED {f}")
    for f in after:
        if f not in before and f not in allowlist:
            v.append(f"UNAUTHORIZED-NEW {f}")
    for f in before:
        if f not in after and f not in allowlist:
            v.append(f"UNAUTHORIZED-DELETED {f}")
    for f in after:
        if f in before and before[f] != after[f] and f not in allowlist:
            v.append(f"UNAUTHORIZED-MODIFIED {f}")
    return (not v), v
