# firmware/glove_esp32

The glove firmware (`glove_esp32.ino`, Arduino IDE). It reads the 5 flex sensors and the MPU6050 at 50 Hz and streams **raw** values to the laptop over USB serial. Calibration and normalization happen on the laptop, so this code rarely changes.

## Serial protocol (frozen v1, 115200 baud)
```
#AIANA,fw=1,rate_hz=50,adc_bits=12,acc_fs=4g,gyr_fs=500dps      boot banner, once
S,<seq>,<t_ms>,<f1..f5>,<ax,ay,az,gx,gy,gz>                    one line per sample
```
- `seq` counts up from 0 (the laptop detects dropped samples from gaps); `t_ms` is `millis()`.
- Flex values are raw ADC counts 0-4095 (thumb to pinky). IMU values are raw int16 (accel +-4 g = 8192 LSB/g, gyro +-500 dps = 65.5 LSB/dps).
- Lines starting with `#` are info or errors. Commands from the laptop, one per line: `PING`, `START`, `STOP`.

## Settings at the top of the sketch
- `SIMULATE_FLEX = true` sends a constant 2048 on the flex channels (use until the flex sensors are connected).
- `STREAM_ON_BOOT = true` streams right away, handy for the Serial Monitor.

## Wiring
Flex sensors on ADC1 pins GPIO 32, 33, 34, 35, 36, each in a voltage divider with a 10k resistor. MPU6050: SDA = GPIO 25, SCL = GPIO 26, VCC = 3V3. Details in [`docs/wiring/`](../../docs/wiring/).

## Status
Draft: not yet compiled or run on real hardware. Test with [`../bringup_tests/`](../bringup_tests/) and `scripts/reader.py` first.
