# firmware

Code that runs on the ESP32 inside the glove.

| Folder | Contents |
|---|---|
| [`glove_esp32/`](glove_esp32/) | The main firmware: streams all sensor values over USB serial at 50 Hz. |
| [`bringup_tests/`](bringup_tests/) | Small sketches to check each part when it arrives (I2C scan, analog inputs). |

Board: ESP32 WROOM-32 38-pin dev board (CP2102 USB-serial, Type-C). Install the Espressif ESP32 package in Arduino IDE Boards Manager and the CP210x driver on Windows. Use a USB **data** cable.
