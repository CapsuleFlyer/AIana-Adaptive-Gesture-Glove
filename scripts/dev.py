#!/usr/bin/env python3
"""Developer helper: the commands we run all the time, in one place.

Run from the repository root:

    python scripts/dev.py doctor   # check the setup: Python, packages, configs, serial ports
    python scripts/dev.py test     # run the tests (same as CI)
    python scripts/dev.py lint     # ruff check (same as CI)
    python scripts/dev.py pins     # check that wiring pins agree across firmware and docs
    python scripts/dev.py all      # lint + test
"""
import argparse
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = ["numpy", "pandas", "scipy", "sklearn", "matplotlib", "yaml", "pytest"]
OPTIONAL = {
    "serial": "pyserial (needed to read the glove)",
    "pyttsx3": "offline text-to-speech",
    "sounddevice": "plays speech into the virtual microphone",
    "pyautogui": "laptop actions",
    "torch": "the 1D-CNN",
}


def have(module):
    try:
        importlib.import_module(module)
        return True
    except Exception:  # missing, or a broken native library (e.g. no audio device in CI)
        return False


def ruff_command():
    """Return the command that runs ruff, or None if it is not installed."""
    probe = subprocess.run(
        [sys.executable, "-m", "ruff", "--version"], capture_output=True, text=True, cwd=ROOT
    )
    if probe.returncode == 0:
        return [sys.executable, "-m", "ruff"]
    exe = shutil.which("ruff")
    return [exe] if exe else None


def doctor():
    problems = 0
    print(f"Python {sys.version.split()[0]} at {sys.executable}")
    in_venv = sys.prefix != sys.base_prefix
    print(f"  virtual environment active: {'yes' if in_venv else 'NO (recommended: python -m venv .venv)'}")
    if sys.version_info < (3, 10):
        print("  WARNING: Python 3.10 or newer is expected")

    print("\nRequired packages")
    for mod in REQUIRED:
        ok = have(mod)
        problems += not ok
        print(f"  {'OK     ' if ok else 'MISSING'} {mod}")

    print("\nOptional packages (only needed for some features)")
    for mod, why in OPTIONAL.items():
        print(f"  {'OK     ' if have(mod) else 'missing'} {mod:12s} {why}")

    print(f"  {'OK     ' if ruff_command() else 'missing'} ruff         the linter for `dev.py lint` (pip install ruff)")

    print("\nConfig files")
    try:
        import yaml

        yaml.safe_load((ROOT / "configs" / "settings.yaml").read_text(encoding="utf-8"))
        print("  OK      configs/settings.yaml")
    except Exception as exc:
        problems += 1
        print(f"  BROKEN  configs/settings.yaml: {exc}")
    try:
        json.loads((ROOT / "configs" / "gestures.json").read_text(encoding="utf-8"))
        print("  OK      configs/gestures.json")
    except Exception as exc:
        problems += 1
        print(f"  BROKEN  configs/gestures.json: {exc}")

    print("\nSerial ports (plug the glove in to see it here)")
    if have("serial"):
        from serial.tools import list_ports

        ports = list(list_ports.comports())
        if not ports:
            print("  none found. Check the USB data cable and the CP210x driver.")
        for p in ports:
            tag = "   <- looks like the ESP32 board" if "CP210" in (p.description or "") else ""
            print(f"  {p.device}: {p.description}{tag}")
    else:
        print("  skipped (pyserial is not installed)")

    print()
    if problems:
        print(f"{problems} problem(s). Fix: pip install -r requirements.txt")
    else:
        print("Setup looks good.")
    return 1 if problems else 0


def run(*args):
    print("$", " ".join(args))
    return subprocess.call(list(args), cwd=ROOT)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("command", choices=["doctor", "test", "lint", "pins", "all"])
    cmd = parser.parse_args().command

    if cmd == "doctor":
        return doctor()
    if cmd == "test":
        return run(sys.executable, "-m", "pytest")
    if cmd == "lint":
        ruff = ruff_command()
        if not ruff:
            print("ruff is not installed. Run: pip install ruff")
            return 1
        return run(*ruff, "check", ".")
    if cmd == "pins":
        return run(sys.executable, "-m", "pytest", "tests/test_pin_consistency.py")

    # all: lint (skipped with a warning if ruff is missing) and then the tests
    ruff = ruff_command()
    lint_status = 0
    if ruff:
        lint_status = run(*ruff, "check", ".")
    else:
        print("WARNING: ruff is not installed, so lint was skipped. Run: pip install ruff")
    return run(sys.executable, "-m", "pytest") or lint_status


if __name__ == "__main__":
    sys.exit(main())
