# Pinout

The single place that says which wire goes where. If you change a pin, change it here, in the firmware, and in the READMEs; `python scripts/dev.py pins` checks that they agree.

Board: ESP32 WROOM-32 **38-pin** dev board (CP2102 USB-serial, Type-C).

## MPU6050 (I2C)

| MPU6050 pin | ESP32 pin | Note |
|---|---|---|
| VCC | 3V3 | Never the `CLK` pin: that is a flash pin, not power |
| GND | GND | |
| SDA | GPIO 25 | |
| SCL | GPIO 26 | |
| AD0, INT, XDA, XCL | not connected | AD0 left open gives address `0x68` |

In code, `Wire.begin(25, 26);` takes (SDA, SCL). The ESP32's default I2C pins are GPIO 21/22, but the breadboard layout leaves the 21/22 header unreachable, so we moved I2C to 25/26.

Status: wired, **not yet verified**. It counts as verified when the scanner prints `Found device at 0x68` and nothing else (see [`bringup-log.md`](bringup-log.md)).

## Flex sensors (analog)

Each sensor sits in a voltage divider with a 10k resistor.

| Finger | GPIO | Silkscreen |
|---|---|---|
| Thumb | 32 | G32 |
| Index | 33 | G33 |
| Middle | 34 | G34 |
| Ring | 35 | G35 |
| Pinky | 36 | SP (also called VP) |

All five are ADC1 pins, which keep working when Wi-Fi or Bluetooth is on. GPIO 34 to 39 are input-only, which is fine for reading a sensor.

Status: not wired yet. `SIMULATE_FLEX = true` in `glove_esp32.ino` until they are.

## Pins to avoid

| Pins | Why |
|---|---|
| GPIO 6 to 11 (`CLK`, `SD0`, `SD1`, `SD2`, `SD3`, `CMD`) | Wired to the board's flash chip |
| GPIO 0, 2, 12, 15 | Boot-strapping pins: a wrong level at power-up can stop the board from starting |
| GPIO 34 to 39 | Input-only: no I2C, no outputs |
| ADC2 pins (25, 26, 27, 14, 12, 13, 4, 2, 15, 0) | Unreliable for analog reads while Wi-Fi or Bluetooth is on (fine for I2C, which is why 25/26 work here) |

## Breadboard layout

The ESP32 straddles the breadboard, so one of its two pin rows is covered. We pushed the board up one row and rotated it so the useful header faces the free holes. Pin labels, in order along each edge:

| Row | Labels |
|---|---|
| Free row (the one jumpers plug into) | 3V3, EN, SP, SN, G34, G35, G32, G33, G25, G26, G27, G14, G12, GND, G13, SD2, SD3, CMD, V5 |
| Covered row | GND, G23, G22, TXD, RXD, G21, GND, G19, G18, G5, G17, 16, G4, G0, G2, G15, SD1, SD0, CLK |

Only one 3V3 and one GND pin are on the free row. Run them to the breadboard's power rails and branch off from there when the flex sensors go in. Some breadboards split their rails in the middle; if half the rail is dead, bridge it with a jumper.

Add a photo of the finished layout to this folder when the wiring is final (the report needs one).
