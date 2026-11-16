"""Build data/raw/manifest.csv (path,user,session,gesture,rep,condition) from all recordings.
Usage: python scripts/build_manifest.py [data/raw]"""
import csv
import json
import re
import sys
from pathlib import Path


def build_manifest(root):
    root = Path(root)
    rows = []
    for udir in sorted(p for p in root.iterdir() if p.is_dir()):
        meta = {}
        if (udir / "session.json").exists():
            meta = json.loads((udir / "session.json").read_text())
        for f in sorted(udir.glob("*.csv")):
            m = re.fullmatch(r"([a-z0-9-]+)_(\d{3})\.csv", f.name)
            if not m:
                print(f"skipping odd file name: {f}")
                continue
            rows.append([f.relative_to(root).as_posix(), udir.name, meta.get("session_id", ""),
                         m.group(1), int(m.group(2)), meta.get("condition", "")])
    with open(root / "manifest.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["path", "user", "session", "gesture", "rep", "condition"])
        w.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    r = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    print(build_manifest(r), "rows written to", Path(r) / "manifest.csv")
