#!/usr/bin/env python3
"""Fail if a human_readable_id was removed, or moved to a different exercise `id`,
since the base ref (default: origin/main).

Consumers treat human_readable_ids as stable lookup keys, so once published an id
must keep pointing at the same exercise forever; it may only be added to a new
exercise after being retired from every other one.
"""

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = ROOT / "exercises"
DEFAULT_BASE = "origin/main"


def run(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True).stdout


def resolve_base(base_ref):
    try:
        run("git", "rev-parse", "--verify", base_ref)
    except subprocess.CalledProcessError:
        print(
            f"error: base ref {base_ref!r} not found locally "
            f"(fetch it first, e.g. `git fetch origin main`)",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        return run("git", "merge-base", "HEAD", base_ref).strip()
    except subprocess.CalledProcessError:
        return base_ref


def load_current():
    mapping = {}
    for path in sorted(EXERCISES_DIR.glob("*/*.yaml")):
        with open(path) as f:
            record = yaml.safe_load(f)
        rel = path.relative_to(ROOT).as_posix()
        for hrid in (record or {}).get("human_readable_ids", []) or []:
            mapping[hrid] = (record.get("id"), rel)
    return mapping


def load_at_ref(ref):
    mapping = {}
    files = run("git", "ls-tree", "-r", "--name-only", ref, "--", "exercises").splitlines()
    for rel in files:
        if not rel.endswith(".yaml"):
            continue
        record = yaml.safe_load(run("git", "show", f"{ref}:{rel}"))
        if not isinstance(record, dict):
            continue
        for hrid in record.get("human_readable_ids", []) or []:
            mapping[hrid] = (record.get("id"), rel)
    return mapping


def main():
    base_ref = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    base_sha = resolve_base(base_ref)

    before = load_at_ref(base_sha)
    after = load_current()

    removed = sorted(hrid for hrid in before if hrid not in after)
    moved = sorted(hrid for hrid in before if hrid in after and before[hrid][0] != after[hrid][0])

    if not removed and not moved:
        print(f"OK: {len(before)} human_readable_ids from {base_ref} ({base_sha[:8]}) all still present and unmoved")
        return 0

    if removed:
        print("Removed human_readable_ids (present at base, missing now):", file=sys.stderr)
        for hrid in removed:
            old_id, old_path = before[hrid]
            print(f"  {hrid}  (was on id={old_id}, {old_path})", file=sys.stderr)

    if moved:
        print("human_readable_ids reassigned to a different exercise:", file=sys.stderr)
        for hrid in moved:
            old_id, old_path = before[hrid]
            new_id, new_path = after[hrid]
            print(f"  {hrid}: id={old_id} ({old_path}) -> id={new_id} ({new_path})", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())
