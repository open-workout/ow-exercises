#!/usr/bin/env python3
"""Resolve duplicate human_readable_ids by suffixing later occurrences with 2, 3, 4, ...

Exercises are processed in ascending `id` (csvId) order, so the exercise with the
lowest id keeps the bare human_readable_id and later ones get "...2", "...3", etc.
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = ROOT / "exercises"


def main():
    paths = sorted(EXERCISES_DIR.glob("*/*.yaml"))
    records = []
    for path in paths:
        with open(path) as f:
            record = yaml.safe_load(f)
        records.append((path, record))

    records.sort(key=lambda pr: int(pr[1]["id"]))

    all_ids = set()
    for _, record in records:
        all_ids.update(record.get("human_readable_ids", []))

    seen_counts = {}
    changed_paths = []

    for path, record in records:
        hrids = record.get("human_readable_ids", [])
        new_hrids = []
        changed = False
        for hrid in hrids:
            seen_counts[hrid] = seen_counts.get(hrid, 0) + 1
            n = seen_counts[hrid]
            if n == 1:
                new_hrids.append(hrid)
                continue

            candidate = f"{hrid}{n}"
            while candidate in all_ids:
                n += 1
                candidate = f"{hrid}{n}"
            all_ids.add(candidate)
            new_hrids.append(candidate)
            changed = True

        if changed:
            print(f"{path.relative_to(ROOT)}: {hrids} -> {new_hrids}")
            record["human_readable_ids"] = new_hrids
            changed_paths.append(path)

    for path, record in records:
        if path in changed_paths:
            with open(path, "w") as f:
                yaml.safe_dump(record, f, sort_keys=False, allow_unicode=True)

    print(f"\nRewrote {len(changed_paths)} files to resolve duplicates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
