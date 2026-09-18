#!/usr/bin/env python3
"""Structural schema validation for exercises/*/*.yaml, run in CI on every PR."""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = ROOT / "exercises"
VOCAB_DIR = ROOT / "vocab"

REQUIRED_KEYS = {
    "id",
    "slug",
    "name",
    "human_readable_ids",
    "primary_muscles",
    "equipment",
    "modalities",
    "load",
}
VALID_MODALITIES = {"reps", "time", "distance"}
VALID_DIRECTIONS = {"added", "assisted"}


def load_vocab(name):
    with open(VOCAB_DIR / name) as f:
        return set(yaml.safe_load(f) or [])


def check_record(path, record, valid_muscles, valid_equipment, seen_ids, seen_slugs):
    errors = []

    if not isinstance(record, dict):
        return [f"{path}: not a YAML mapping"]

    missing = REQUIRED_KEYS - record.keys()
    if missing:
        errors.append(f"{path}: missing required keys: {sorted(missing)}")
        return errors  # further checks assume presence

    expected_slug = path.stem
    if record["slug"] != expected_slug:
        errors.append(f"{path}: slug {record['slug']!r} does not match filename {expected_slug!r}")

    if record["id"] in seen_ids:
        errors.append(f"{path}: duplicate id {record['id']!r} (also used by {seen_ids[record['id']]})")
    else:
        seen_ids[record["id"]] = path

    if record["slug"] in seen_slugs:
        errors.append(f"{path}: duplicate slug {record['slug']!r} (also used by {seen_slugs[record['slug']]})")
    else:
        seen_slugs[record["slug"]] = path

    if not isinstance(record["human_readable_ids"], list) or not record["human_readable_ids"]:
        errors.append(f"{path}: human_readable_ids must be a non-empty list")
    else:
        for hrid in record["human_readable_ids"]:
            if isinstance(hrid, str) and hrid[:1].isdigit():
                errors.append(f"{path}: human_readable_id {hrid!r} must not begin with a digit")

    if not isinstance(record["primary_muscles"], list):
        errors.append(f"{path}: primary_muscles must be a list")
    else:
        bad = set(record["primary_muscles"]) - valid_muscles
        if bad:
            errors.append(f"{path}: primary_muscles not in vocab/muscles.yaml: {sorted(bad)}")

    if not isinstance(record["equipment"], list):
        errors.append(f"{path}: equipment must be a list")
    else:
        bad = set(record["equipment"]) - valid_equipment
        if bad:
            errors.append(f"{path}: equipment not in vocab/equipment.yaml: {sorted(bad)}")

    modalities = record["modalities"]
    if not isinstance(modalities, list) or not modalities or set(modalities) - VALID_MODALITIES:
        errors.append(f"{path}: modalities must be a non-empty subset of {sorted(VALID_MODALITIES)}, got {modalities!r}")

    load = record["load"]
    if not isinstance(load, dict) or "required" not in load or "direction" not in load:
        errors.append(f"{path}: load must be a mapping with 'required' and 'direction'")
    else:
        if not isinstance(load["required"], bool):
            errors.append(f"{path}: load.required must be a boolean")
        if load["direction"] not in VALID_DIRECTIONS:
            errors.append(f"{path}: load.direction must be one of {sorted(VALID_DIRECTIONS)}, got {load['direction']!r}")

    return errors


def main():
    valid_muscles = load_vocab("muscles.yaml")
    valid_equipment = load_vocab("equipment.yaml")

    seen_ids = {}
    seen_slugs = {}
    all_errors = []
    count = 0

    for path in sorted(EXERCISES_DIR.glob("*/*.yaml")):
        count += 1
        with open(path) as f:
            record = yaml.safe_load(f)
        rel_path = path.relative_to(ROOT)
        all_errors.extend(check_record(rel_path, record, valid_muscles, valid_equipment, seen_ids, seen_slugs))

    if all_errors:
        print(f"Found {len(all_errors)} schema error(s) across {count} files:", file=sys.stderr)
        for err in all_errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print(f"OK: {count} exercise files pass schema validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
