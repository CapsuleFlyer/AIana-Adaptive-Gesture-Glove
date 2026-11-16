"""Minimal glove reader: reads the ESP32 serial stream, checks it, prints a live summary.

Usage:   python reader.py            (auto-finds the CP210x port)
         python reader.py COM5       (or give the port yourself)
IMPORTANT: close the Arduino Serial Monitor first, only one program can use the port.
Stop with Ctrl+C.
"""
import sys
import time

import serial
from serial.tools import list_ports

ACC_LSB_PER_G = 8192.0    # +-4 g   (must match the banner / firmware)
GYR_LSB_PER_DPS = 65.5    # +-500 dps


def find_port():
    for p in list_ports.comports():
        text = f"{p.description} {p.manufacturer}"
        if "CP210" in text or "Silicon Labs" in text:
            return p.device
    return None


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_port()
    if port is None:
        print("No CP210x port found. Plug in the ESP32 (data cable) or pass the port: python reader.py COM5")
        print("Ports seen:", [p.device for p in list_ports.comports()])
        sys.exit(1)

    print(f"Opening {port} at 115200 ...")
    ser = serial.Serial(port, 115200, timeout=1)
    time.sleep(0.5)
    ser.reset_input_buffer()

    expected = None
    total = drops = bad = 0
    last = None
    window_start = time.time()
    window_count = 0

    try:
        while True:
            line = ser.readline().decode("ascii", errors="ignore").strip()
            if not line:
                continue
            if line.startswith("#"):
                print(line)
                continue
            parts = line.split(",")
            if parts[0] != "S" or len(parts) != 14:
                bad += 1
                continue
            try:
                vals = [int(x) for x in parts[1:]]
            except ValueError:
                bad += 1
                continue

            seq = vals[0]
            if expected is not None and seq > expected:
                drops += seq - expected
            expected = seq + 1
            total += 1
            window_count += 1
            last = vals

            now = time.time()
            if now - window_start >= 1.0:
                rate = window_count / (now - window_start)
                flex = last[2:7]
                ax, ay, az, gx, gy, gz = last[7:13]
                print(
                    f"{rate:5.1f} Hz | total {total} drops {drops} bad {bad} | flex {flex} | "
                    f"acc g ({ax / ACC_LSB_PER_G:+.2f},{ay / ACC_LSB_PER_G:+.2f},{az / ACC_LSB_PER_G:+.2f}) | "
                    f"gyro dps ({gx / GYR_LSB_PER_DPS:+.0f},{gy / GYR_LSB_PER_DPS:+.0f},{gz / GYR_LSB_PER_DPS:+.0f})"
                )
                window_start = now
                window_count = 0
    except KeyboardInterrupt:
        print(f"\nStopped. total={total} drops={drops} bad={bad}")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
