# src/aiana/preprocessing

Turning raw sensor data into model input.

Written so far (`signspeak.py`):
- `load_signspeak()`: reads `data/external/SignSpeakDataset.csv` into `X (N, 64, 5)`. The column layout is an unverified guess: check it with `scripts/inspect_dataset.py`.
- `per_user_minmax()`: scales each sensor to 0-1 per user (needed because hands differ and ADC ranges differ).

Resampling to a fixed 64 steps lives in `acquisition/reader.py` (`resample()`).

Planned: low-pass filtering, feature extraction for the baselines, building `.npz` files for our own recordings.
Channels are 5 (flex only, SignSpeak) or 11 (flex + 6 IMU axes, our glove).
