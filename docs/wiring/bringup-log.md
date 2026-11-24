# Hardware bring-up log

What we tested on the real hardware, in order, and what happened. Add an entry whenever a test is run. This feeds the "testing and results" and "hardware description" parts of the report.

## Status board

| Check | Status |
|---|---|
| ESP32 board powers, is detected (CP2102 driver) and flashes from the Arduino IDE | Done (Nov 23) |
| MPU6050 powered (power LED on) | Done (Nov 23) |
| MPU6050 found by the I2C scanner at `0x68` | **Pending**: header pins need soldering |
| `glove_esp32.ino` streams IMU data (accel near 0, 0, +-8192 when flat) | Pending |
| Flex sensors wired, `02_adc_test` run | Pending |
| `scripts/reader.py` sees 50 Hz with no dropped samples | Pending |

## Nov 23, 2026

**ESP32 flashed.** Board: ESP32-D0WD-V3 (rev v3.1), 38-pin, Type-C. Arduino IDE 2.3.11, esp32 core 3.3.12, esptool 5.3.1, port COM5. The first upload failed with `Could not open COM5 ... device not functioning`. It worked after holding BOOT during `Connecting...`. The scanner sketch used 22% of flash and 7% of RAM.

**Layout decision.** With the board in its first breadboard position, neither pin row had free holes. We moved it up one row and rotated it 180 degrees so the `3V3 / G25 / G26 / G32 to G36` header is on the free row. The default I2C pins (21/22) became unreachable, so I2C moved to **GPIO 25 / 26** and every sketch and README was changed to match.

**Wiring slip, caught.** VCC was first plugged into the pin labelled `CLK`, which is a flash pin and not a power pin. It was removed. The board still boots and flashes normally.

**MPU6050 not detected.** The scanner printed `No I2C devices found` repeatedly while the module's power LED was on, so power was reaching it but the data lines were not.

- A pin-state test (`pinMode` INPUT, `digitalRead` on GPIO 25 and 26) first showed SDA steady at 1 while SCL flipped between 0 and 1, then both lines flipping together. Healthy, connected lines hold a steady 1 because the module has pull-up resistors.
- With `INPUT_PULLUP` both read 1 all the time. That proves nothing about the module, only that the lines were not shorted to each other.
- While the module was being moved by hand, the scanner briefly reported `0x06`, `0x0F`, `0x10`, `0x11`. These are not the MPU6050's address (`0x68`); they are noise from a half-connected bus.

**Cause.** The module's header pins were resting in the holes, not soldered. **Fix:** solder the header (planned Nov 24), then rerun `01_i2c_scanner`. If a clean scan still fails, try `Wire.begin(26, 25);` in case SDA and SCL are crossed.

## Next entries

- Nov 24: after soldering, scanner result (expect `Found device at 0x68` only).
- Then `glove_esp32.ino` serial output, flex wiring and `02_adc_test`, and `scripts/reader.py` rate check.
