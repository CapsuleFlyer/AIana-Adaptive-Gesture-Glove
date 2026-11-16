# tests

Automated tests. Run from the repository root: `python -m pytest tests`. None of them needs the glove.

| File | Covers |
|---|---|
| `test_reader.py` | Serial line parsing (good and bad lines), the fake source, windowing, resampling, drop counting, CSV replay. |
| `test_actions.py` | Gesture-to-action lookup, risky actions needing confirm, cancel/timeout/cooldown, the `Normalizer` and `StubRecognizer`. |

Still to add: the conflict checker flags two nearly identical gestures.
Also keep a manual test log (what we tried, what happened). The course asks for evidence that the system was tested with representative inputs.
