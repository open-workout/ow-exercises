#!/usr/bin/env python3
"""Bundle every exercise YAML plus vocab into a single JSON file for releases."""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
EXERCISES_DIR = ROOT / "exercises"
VOCAB_DIR = ROOT / "vocab"
DEFAULT_OUT = ROOT / "dist" / "exercises-bundle.json"


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT

    exercises = []
    for path in sorted(EXERCISES_DIR.glob("*/*.yaml")):
        with open(path) as f:
            exercises.append(yaml.safe_load(f))

    vocab = {}
    for path in sorted(VOCAB_DIR.glob("*.yaml")):
        with open(path) as f:
            vocab[path.stem] = yaml.safe_load(f)

    bundle = {"exercises": exercises, "vocab": vocab}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(bundle, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(exercises)} exercises and {len(vocab)} vocab lists to {out_path}")


if __name__ == "__main__":
    main()
