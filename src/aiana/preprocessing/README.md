# src/aiana/preprocessing

**This is where cleaning and normalizing the sensor data will happen.**

**Owner:** `____`  **Status:** not started

## What goes here
- Low-pass filtering of flex and IMU signals
- Padding or resampling every recording to a fixed length
- **Per-user normalization/calibration** (scale each sensor to 0-1 per person). Needed because hands differ and the ESP32 ADC (12-bit) differs from the Arduino readings in SignSpeak (10-bit).
- A loader for the SignSpeak CSV (reshape to time steps x 5 sensors)
- Feature extraction for the baseline models (mean, variance, min/max per channel)

Keep the number of channels configurable: 5 (flex only, SignSpeak) or 11 (flex + 6 IMU axes, our glove).
