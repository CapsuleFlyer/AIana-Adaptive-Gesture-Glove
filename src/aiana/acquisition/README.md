# src/aiana/acquisition

Getting glove data into Python.

`reader.py` provides:
- `read_samples(kind, ...)`: one interface for three sources: `"serial"` (the real glove), `"replay"` (a recorded CSV), `"fake"` (generated data). The rest of the app does not care which one it gets, so everyone can develop without the glove.
- `parse_line()`: turns one serial line into a `Sample`; info lines and malformed lines return `None`.
- `Windower`: sliding window over the stream (default 2.0 s = 100 samples, stride 12 samples).
- `resample()`: stretches or shrinks a window to a fixed 64 steps.
- `count_drops()`: counts missing sequence numbers.

Still to do: auto-reconnect when the cable is unplugged mid-demo, and optional Bluetooth.
Tests: `tests/test_reader.py`.
