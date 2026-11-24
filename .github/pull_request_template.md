## What changed

<!-- One or two sentences. -->

## Why

<!-- The problem this solves, or the task from project-flow.md. -->

## Checklist

- [ ] `python scripts/dev.py all` passes
- [ ] I tested it (on the glove, or with `--source fake` / `--synthetic` if no glove)
- [ ] This does **not** change a frozen interface (serial line, recording CSV, Recognizer API)
  - [ ] ...or it does, and I have told the group
- [ ] If I changed a pin: firmware, READMEs and `docs/wiring/pinout.md` all match (`python scripts/dev.py pins`)
- [ ] No keys, personal data or volunteer names are included
- [ ] I can explain every line of this change
