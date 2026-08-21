"""Sealed-holdout tooling (design section 7). The seal is a hash manifest
committed BEFORE the first run; contents never publish."""
import hashlib, json, os, sys

def seal(fixtures_dir, manifest_out):
    """Hash every fixture file; write the manifest. Fail if manifest exists
    and any hash changed (tamper-evidence)."""
    entries = {}
    for root, _, files in os.walk(fixtures_dir):
        for f in sorted(files):
            path = os.path.join(root, f)
            rel = os.path.relpath(path, fixtures_dir)
            h = hashlib.sha256(open(path, "rb").read()).hexdigest()
            entries[rel] = h
    manifest = {"n": len(entries), "files": entries}
    if os.path.exists(manifest_out):
        old = json.load(open(manifest_out))
        if old != manifest:
            print("SEAL MISMATCH — fixture set changed after sealing", file=sys.stderr)
            return 2
        print(f"SEAL VERIFIED ({len(entries)} fixtures unchanged)")
        return 0
    with open(manifest_out, "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print(f"SEALED {len(entries)} fixtures -> {manifest_out}")
    return 0

if __name__ == "__main__":
    sys.exit(seal(sys.argv[1], sys.argv[2]))
