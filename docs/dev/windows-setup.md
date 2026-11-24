# Windows setup

From a fresh laptop to a flashed glove.

## 1. Python side

```powershell
git clone <repo-url>
cd AIana-Adaptive-Gesture-Glove
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt        # full set, includes PyTorch (large download)
# or, for tests and baselines only:
pip install -r requirements-ci.txt
python scripts/dev.py doctor           # should end with "Setup looks good."
python scripts/dev.py all              # lint + tests
```

If PowerShell refuses to run the activate script: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## 2. Glove side (Arduino IDE 2)

1. Install the **CP210x USB driver** from Silicon Labs. The board uses a CP2102 chip. After plugging in, "Silicon Labs CP210x" should appear in Device Manager under *Ports (COM & LPT)*.
2. Use a USB **data** cable. Charge-only cables are the most common reason a board never shows up.
3. In *File > Preferences*, add this to "Additional boards manager URLs":
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
4. *Tools > Board > Boards Manager*, install **esp32 by Espressif Systems** (we use 3.3.12).
5. *Tools > Board > ESP32 Dev Module*, and pick the COM port under *Tools > Port*.
6. Serial Monitor at **115200 baud**.
7. Run the sketches in `firmware/bringup_tests/` in order, then `firmware/glove_esp32/`.

CI compiles every sketch with the same board and core version, so a green check means the code at least builds.

## 3. VS Code without the red squiggle

Opening an `.ino` file in VS Code shows `cannot open source file "Wire.h"`. That is only the editor not knowing where the ESP32 libraries live. It does not affect compiling in the Arduino IDE. To silence it, create `.vscode/c_cpp_properties.json` (the `.vscode/` folder is git-ignored, so this stays on your machine):

```json
{
  "version": 4,
  "configurations": [
    {
      "name": "ESP32",
      "includePath": [
        "${workspaceFolder}/**",
        "${env:LOCALAPPDATA}/Arduino15/packages/esp32/hardware/esp32/3.3.12/cores/esp32",
        "${env:LOCALAPPDATA}/Arduino15/packages/esp32/hardware/esp32/3.3.12/variants/esp32",
        "${env:LOCALAPPDATA}/Arduino15/packages/esp32/hardware/esp32/3.3.12/libraries/**"
      ],
      "cppStandard": "c++17"
    }
  ]
}
```

Adjust `3.3.12` if you installed a different core version. A few other warnings can remain; the Arduino IDE (or the CI job) is the source of truth for whether the code builds.

## 4. Errors we have already hit

| Message or symptom | Cause and fix |
|---|---|
| `Could not open COM5, the port is busy or doesn't exist` (`PermissionError 13`) | Another program holds the port: close the Serial Monitor, VS Code terminals and any `reader.py` / `record.py`. If it persists, replug the board, check *Tools > Port* (the number can change), and try another cable. |
| Upload hangs on `Connecting...` | Hold the **BOOT** button on the board until writing starts, then release. |
| Serial Monitor shows garbage characters | Baud rate is not 115200. |
| Scanner prints `No I2C devices found` while the sensor's power LED is on | Power reaches the sensor but the data lines do not. Check SDA and SCL jumper columns, and that the module's header pins are **soldered** (resting pins give flaky contact). |
| Scanner shows random addresses such as `0x06`, `0x0F`, `0x10` | Noise from a loose connection. The MPU6050 shows up as exactly `0x68` (or `0x69`). |
| Wire is plugged into a pin called `CLK`, `SD0`, `SD1`, `SD2`, `SD3` or `CMD` | Those are the flash chip's pins (GPIO 6 to 11). Never connect anything to them. |

Full wiring details: [`../wiring/pinout.md`](../wiring/pinout.md).
