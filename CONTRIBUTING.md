# Contributing

This repo tracks one exercise per YAML file under `exercises/<xx>/<slug>.yaml`, where
`<xx>` is the first two characters of the slug. The filename is the canonical slug and
never moves.

## What you can contribute

- `alt_names`: alternate names for an exercise, keyed by language code (`en`, `es`, ...).
- Corrections to `primary_muscles` or `equipment` (values must come from
  `vocab/muscles.yaml` / `vocab/equipment.yaml` — see below if the value you need is missing).
- Anything else added to an exercise file beyond the core generated fields (`id`, `slug`,
  `name`, `human_readable_ids`, `primary_muscles`, `equipment`, `modalities`, `load`).

`vocab/muscles.yaml` and `vocab/equipment.yaml` (the controlled vocabularies) are
maintainer-owned (see `CODEOWNERS`) — open an issue if you need a new value added there
before using it in an exercise file.

Do not edit `exercises.json` — it's a private source dump used only by maintainers to
regenerate the tree, and it isn't tracked in git.

## Before opening a PR

1. Keep PRs small and focused — ideally one exercise, or one kind of change (e.g. adding
   Spanish alt_names) across a handful of files. Small PRs are easier to review and
   essentially never conflict with anyone else's PR, since each exercise lives in its own file.
2. Run the validation scripts locally:
   ```
   python3 scripts/validate_exercises.py
   python3 scripts/check_unique_human_readable_ids.py
   ```
   Both must pass — they also run in CI on every PR.
3. Open the PR against `main`. It needs a passing CI run and one maintainer approval to merge.

## Release cadence

`main` merges continuously as PRs are approved. Downstream apps that want a stable,
infrequently-changing snapshot should pin to a tagged release (published monthly) rather
than tracking `main` directly.
