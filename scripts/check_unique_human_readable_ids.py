#!/usr/bin/env python3
"""Fail if any human_readable_id is reused across exercise YAML files."""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = ROOT / "exercises"


def main():
    seen = {}
    duplicates = {}

    for path in sorted(EXERCISES_DIR.glob("*/*.yaml")):
        with open(path) as f:
            record = yaml.safe_load(f)

        for hrid in record.get("human_readable_ids", []):
            if hrid in seen:
                duplicates.setdefault(hrid, {seen[hrid]}).add(path.relative_to(ROOT))
            else:
                seen[hrid] = path.relative_to(ROOT)

    if duplicates:
        print("Duplicate human_readable_ids found:", file=sys.stderr)
        for hrid, paths in sorted(duplicates.items()):
            print(f"  {hrid}:", file=sys.stderr)
            for p in sorted(paths):
                print(f"    - {p}", file=sys.stderr)
        return 1

    print(f"OK: {len(seen)} unique human_readable_ids across {sum(1 for _ in EXERCISES_DIR.glob('*/*.yaml'))} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
