# src/aiana/acquisition

**This is where the code that reads the glove will go.**

**Owner:** `____`  **Status:** not started

## What goes here
- A reader for the ESP32 stream (USB serial first, BLE later)
- Parsing each sample line into numbers
- Cutting the stream into fixed-length windows (sliding window, size and stride from `configs/settings.yaml`)
- Auto-reconnect if the connection drops mid-demo
- A recorder script that saves labeled samples into `data/raw/<user>/`

## Idea to check out
Lexicon Glove keeps a sliding 2-second window and shifts it by one sample each time. See its Neural Network wiki page (linked in the main README).
