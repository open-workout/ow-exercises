#!/usr/bin/env python3
"""Export exercises/*.yaml as a flat JSON array for downstream consumers.

Unlike export_bundle.py (which dumps every YAML field plus vocab), this only
emits the fields a consumer needs to render an exercise picker.
"""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = ROOT / "exercises"
DEFAULT_OUT = ROOT / "dist" / "exercises.json"


def to_entry(record):
    modalities = record.get("modalities", [])
    return {
        "csvId": record["id"],
        "name": record["name"],
        "alt_names": record.get("alt_names", {}),
        "human_readable_ids": record["human_readable_ids"],
        "primary_muscles": record["primary_muscles"],
        "equipment": record["equipment"],
        "canBeDoneInReps": "reps" in modalities,
        "canBeDoneInTime": "time" in modalities,
        "canBeDoneInDistance": "distance" in modalities,
        "requiresWeight": record["load"]["required"],
    }


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT

    entries = []
    for path in sorted(EXERCISES_DIR.glob("*/*.yaml")):
        with open(path) as f:
            record = yaml.safe_load(f)
        entries.append(to_entry(record))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(entries)} exercises to {out_path}")


if __name__ == "__main__":
    main()
