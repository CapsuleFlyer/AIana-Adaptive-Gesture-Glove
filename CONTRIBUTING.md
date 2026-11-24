# Contributing

Short version of how we work. The course rule applies to everything: other people's projects are **reference only**; we write our own code and cite what we learn from.

## Before you push

```bash
python scripts/dev.py doctor   # is my setup healthy?
python scripts/dev.py all      # lint + tests, the same checks CI runs
```

If you touched a pin number, run `python scripts/dev.py pins`. It checks that the two sketches, every README and the wiring docs all agree.

## Branches and pull requests

- Work on your own branch: `p1/<topic>`, `p2/<topic>`, `p3/<topic>` (your role from [`project-flow.md`](project-flow.md)), then open a pull request into `dev`.
- Keep PRs small: one thing each. Commit often.
- **Interfaces are frozen** (serial line, recording CSV, Recognizer API in `project-flow.md` section 2). Changing one needs a PR **and** a message to the group, and the PR template has a box for it.
- Another member reviews before merge. Everyone must be able to explain what they merged.

## Commit messages

One line, present tense, say what changed and where: `firmware: move I2C to GPIO 25/26`, `reader: detect dropped samples`, `docs: add bring-up log`.

## What goes where

| Kind of change | Where |
|---|---|
| Glove firmware and bring-up sketches | `firmware/` |
| Python pipeline | `src/aiana/` |
| One-off command-line tools | `scripts/` |
| Wiring, photos, pin table, bring-up log | `docs/wiring/` |
| Setup help | `docs/dev/` |

## Keep out of the repo

API keys, personal data, volunteer names (use `user01`, `user02`, ...), large datasets and model files (they are git-ignored on purpose).
