# configs

Settings shared by the whole project. Change them only through a pull request, because every part of the app reads them.

| File | What it holds |
|---|---|
| `gestures.json` | Which gesture triggers which action: a spoken phrase (`speak`) or a laptop action (`laptop`). Also names the `confirm` and `cancel` gestures. Risky laptop actions (`needs_confirm: true`) only run after the confirm gesture. |
| `settings.yaml` | Sample rate, window length, preprocessing, model and few-shot settings, conflict-checker threshold, speech settings (virtual mic device name), evaluation setup. |

**Note:** the gestures in `gestures.json` are examples until the gesture list is locked after the pilot. The values in `settings.yaml` are starting guesses. When you tune one, write down what changed and why.

Used by: `src/aiana/actions/` (reads `gestures.json`), the app and training code (read `settings.yaml`).
