# src/aiana/actions

What happens after a gesture is recognized.

| File | Role |
|---|---|
| `dispatcher.py` | `ActionDispatcher`: looks the gesture up in `configs/gestures.json` and runs the speech or laptop action. Risky laptop actions wait for the confirm gesture (5 s timeout). Cancel, any other gesture or a timeout drops them. A 1.5 s cooldown stops double triggers. |
| `speech.py` | Text-to-speech (pyttsx3, offline) saved to a WAV, cached per phrase, played with sounddevice to the **"CABLE Input"** device (VB-CABLE). In Meet/Zoom choose **"CABLE Output"** as the microphone. |
| `laptop.py` | Laptop actions through pyautogui (scroll, key combinations). Moving the mouse to a screen corner aborts. |

The dispatcher takes the speak and laptop functions as arguments, so it is tested with fakes.
Try speech and latency with `python scripts/speech_test.py`. Tests: `tests/test_actions.py`.
