# src/aiana/actions

**This is where what happens after a gesture is recognized will go.**

**Owner:** `____`  **Status:** not started

## What goes here
- **Speech:** text-to-speech (pyttsx3 offline, gTTS for Urdu) played to a **virtual microphone** (VB-CABLE) so Zoom/Meet/WhatsApp hear it as the user's voice. Cache repeated phrases to cut latency.
- **Laptop actions:** a small set of 5-8 actions through pyautogui (scroll, next/previous tab, play/pause, open an app, and so on)
- **Safety:** risky actions (close window, send) need the confirm gesture first, and a cancel gesture backs out
- The lookup that reads `configs/gestures.json` and decides which action a gesture triggers (this mapping is a lookup table, not the ML part)

## Setup notes
- Install VB-CABLE (Windows), then choose "CABLE Output" as the microphone in the call app
- Reference: LiveLingo and VoiceConductor (links in the main README)
