# firmware/glove_esp32

**This is where the ESP32 code will go.**

**Owner:** `____`  **Status:** not started

## What goes here
- The Arduino/PlatformIO sketch that reads the 5 flex sensors (analog) and the MPU6050 (I2C)
- Fixed-rate sampling (rate set in `configs/settings.yaml`)
- Sending each sample to the laptop over USB serial first, Bluetooth later
- A simple calibration routine (open hand / closed fist)

## Notes
- Put flex sensors on **ADC1 pins**. ADC2 pins can conflict with WiFi/Bluetooth.
- Each flex sensor needs a resistor in a voltage divider (the build guides use 10k).
- Use a USB **data** cable, not a charge-only one.
- Keep the printed data format simple and documented here, for example one line per sample:
  `timestamp_ms,flex1,flex2,flex3,flex4,flex5,ax,ay,az,gx,gy,gz`
- Reference starting points: see the "GloveTalk" and "Magic Wand" links in the main README. Write our own code and cite them.
