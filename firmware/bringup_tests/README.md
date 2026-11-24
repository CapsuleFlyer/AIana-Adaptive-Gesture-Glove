# firmware/bringup_tests

Small Arduino sketches to check hardware step by step. Run them in this order, each one at 115200 baud in the Serial Monitor.

| Sketch | Checks | Expected result |
|---|---|---|
| `01_i2c_scanner/` | MPU6050 wiring (VCC to 3V3, SDA to GPIO 25, SCL to GPIO 26) | `Found device at 0x68` |
| `02_adc_test/` | The five analog inputs (GPIO 32, 33, 34, 35, 36) | A 10k + 10k divider reads about 2000-2100; an unconnected pin reads noisy garbage |

Once both pass, flash [`../glove_esp32/`](../glove_esp32/) and run `scripts/reader.py`.
