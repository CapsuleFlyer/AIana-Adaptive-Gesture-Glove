"""The wiring pins must agree everywhere: both sketches, every README, the wiring docs.

This exists because the I2C pins were changed (21/22 -> 25/26) when the breadboard layout
forced it, and the old numbers were still sitting in five places. If this test fails, a pin
was changed in one place but not in the others.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GLOVE = ROOT / "firmware" / "glove_esp32" / "glove_esp32.ino"
SCANNER = ROOT / "firmware" / "bringup_tests" / "01_i2c_scanner" / "01_i2c_scanner.ino"
ADC_TEST = ROOT / "firmware" / "bringup_tests" / "02_adc_test" / "02_adc_test.ino"

WIRE_BEGIN = re.compile(r"Wire\.begin\(\s*(\d+)\s*,\s*(\d+)\s*\)")
SDA_MENTION = re.compile(r"\bSDA\b\s*(?:=|->|to)\s*(?:GPIO\s*)?(\d+)", re.IGNORECASE)
SCL_MENTION = re.compile(r"\bSCL\b\s*(?:=|->|to)\s*(?:GPIO\s*)?(\d+)", re.IGNORECASE)
PIN_ARRAY = re.compile(r"(?:FLEX_PINS|PINS)\s*\[\s*5\s*\]\s*=\s*\{([^}]*)\}")

ADC1_PINS = {32, 33, 34, 35, 36, 37, 38, 39}  # ADC2 is unreliable while Wi-Fi/Bluetooth is on
FLASH_PINS = set(range(6, 12))                # GPIO 6-11 are wired to the board's flash chip


def wire_pins(path):
    match = WIRE_BEGIN.search(path.read_text(encoding="utf-8"))
    assert match, f"no Wire.begin(sda, scl) found in {path.name}"
    return int(match.group(1)), int(match.group(2))


def doc_files():
    files = list((ROOT / "firmware").rglob("*.ino")) + list((ROOT / "firmware").rglob("*.md"))
    files += list((ROOT / "docs" / "wiring").glob("*.md"))
    return files


def flex_pins(path):
    match = PIN_ARRAY.search(path.read_text(encoding="utf-8"))
    assert match, f"no 5-pin array found in {path.name}"
    return [int(p) for p in match.group(1).replace(" ", "").split(",") if p]


def test_both_sketches_use_the_same_i2c_pins():
    assert wire_pins(GLOVE) == wire_pins(SCANNER)


def test_every_doc_and_comment_matches_the_sketch_pins():
    sda, scl = wire_pins(GLOVE)
    wrong = []
    for path in doc_files():
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for regex, expected, name in ((SDA_MENTION, sda, "SDA"), (SCL_MENTION, scl, "SCL")):
                for found in regex.findall(line):
                    if int(found) != expected:
                        rel = path.relative_to(ROOT)
                        wrong.append(f"{rel}:{number} says {name} = {found}, sketch uses {expected}")
    assert not wrong, "pin mismatch:\n  " + "\n  ".join(wrong)


def test_i2c_pins_are_safe_choices():
    sda, scl = wire_pins(GLOVE)
    assert sda != scl
    assert not ({sda, scl} & FLASH_PINS), "GPIO 6-11 are used by the flash chip"
    assert not ({sda, scl} & {34, 35, 36, 37, 38, 39}), "GPIO 34-39 are input-only, so no I2C"


def test_flex_pins_match_between_sketches_and_use_adc1():
    glove, adc = flex_pins(GLOVE), flex_pins(ADC_TEST)
    assert glove == adc
    assert len(set(glove)) == 5
    assert set(glove) <= ADC1_PINS, "flex sensors must be on ADC1 pins"
    assert not (set(glove) & set(wire_pins(GLOVE))), "a flex pin clashes with an I2C pin"
