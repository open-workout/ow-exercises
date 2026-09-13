#!/usr/bin/env python3
"""Generate per-exercise YAML files and vocab lists from exercises.json."""

import json
import re
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "exercises.json"
EXERCISES_DIR = ROOT / "exercises"
VOCAB_DIR = ROOT / "vocab"

DIRECTION_MAP = {1: "added", -1: "assisted"}

# Fields fully derived from exercises.json on every run. Anything else a
# contributor adds to a file (e.g. alt_names) is not one of these, so it
# survives regeneration - see load_existing_extras()/CANONICAL_FIELDS below.
CANONICAL_FIELDS = {
    "id",
    "slug",
    "name",
    "human_readable_ids",
    "primary_muscles",
    "equipment",
    "modalities",
    "load",
}


def load_existing_extras():
    """Map csvId -> contributor-added fields (e.g. alt_names) from the current
    exercises/ tree, keyed by id (not slug, since a refreshed name can change
    the slug) so they survive a full regeneration."""
    extras_by_id = {}
    if not EXERCISES_DIR.exists():
        return extras_by_id
    for path in EXERCISES_DIR.glob("*/*.yaml"):
        with open(path) as f:
            record = yaml.safe_load(f) or {}
        extras = {k: v for k, v in record.items() if k not in CANONICAL_FIELDS}
        if extras:
            extras_by_id[record["id"]] = extras
    return extras_by_id


def slugify(name):
    s = name.lower().replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    s = re.sub(r"-+", "-", s)
    return s


def build_modalities(entry):
    modalities = []
    if entry["canBeDoneInReps"]:
        modalities.append("reps")
    if entry["canBeDoneInTime"]:
        modalities.append("time")
    if entry["canBeDoneInDistance"]:
        modalities.append("distance")
    return modalities


def main():
    with open(JSON_PATH) as f:
        data = json.load(f)

    extras_by_id = load_existing_extras()

    # First pass: compute base slugs and detect collisions.
    base_slugs = [slugify(entry["name"]) for entry in data]
    counts = {}
    for s in base_slugs:
        counts[s] = counts.get(s, 0) + 1

    final_slugs = []
    disambiguated = []
    for entry, base in zip(data, base_slugs):
        if counts[base] > 1:
            slug = f"{base}-{entry['csvId']}"
            disambiguated.append((base, slug))
        else:
            slug = base
        final_slugs.append(slug)

    # Vocab
    muscles = set()
    equipment = set()
    for entry in data:
        muscles.update(entry["primaryMuscles"])
        muscles.update(entry["secondaryMuscles"])
        equipment.update(entry["equipment"])

    if VOCAB_DIR.exists():
        shutil.rmtree(VOCAB_DIR)
    VOCAB_DIR.mkdir(parents=True)
    with open(VOCAB_DIR / "muscles.yaml", "w") as f:
        yaml.safe_dump(sorted(muscles), f, sort_keys=False, allow_unicode=True)
    with open(VOCAB_DIR / "equipment.yaml", "w") as f:
        yaml.safe_dump(sorted(equipment), f, sort_keys=False, allow_unicode=True)

    # Exercises
    if EXERCISES_DIR.exists():
        shutil.rmtree(EXERCISES_DIR)
    EXERCISES_DIR.mkdir(parents=True)

    for entry, slug in zip(data, final_slugs):
        extras = extras_by_id.get(entry["csvId"], {})
        extras.setdefault("alt_names", {})
        extras["alt_names"].setdefault("en", [])

        record = {
            "id": entry["csvId"],
            "slug": slug,
            "name": entry["name"],
            **extras,
            "human_readable_ids": [entry["humanReadableId"]],
            "primary_muscles": entry["primaryMuscles"],
            "equipment": entry["equipment"],
            "modalities": build_modalities(entry),
            "load": {
                "required": entry["requiresWeight"],
                "direction": DIRECTION_MAP[entry["weightDirection"]],
            },
        }

        subdir = EXERCISES_DIR / slug[:2]
        subdir.mkdir(parents=True, exist_ok=True)
        out_path = subdir / f"{slug}.yaml"
        with open(out_path, "w") as f:
            yaml.safe_dump(record, f, sort_keys=False, allow_unicode=True)

    print(f"Wrote {len(data)} exercise YAML files under {EXERCISES_DIR}")
    print(f"Wrote vocab/muscles.yaml ({len(muscles)} entries)")
    print(f"Wrote vocab/equipment.yaml ({len(equipment)} entries)")
    print(f"Disambiguated {len(disambiguated)} slugs via csvId suffix:")
    for base, slug in sorted(disambiguated):
        print(f"  {base} -> {slug}")


if __name__ == "__main__":
    main()
