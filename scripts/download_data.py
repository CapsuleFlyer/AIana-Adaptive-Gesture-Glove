"""One-time download of the external datasets into data/external/ (git-ignored, so everyone runs this once).

  python scripts/download_data.py            download what is missing
  python scripts/download_data.py --force    download again

Datasets: SignSpeak (Harvard Dataverse, DOI 10.7910/DVN/ODY7GH, CC0) -> data/external/SignSpeakDataset.csv
Our own glove recordings are not downloaded: they are made with scripts/record.py.
Uses only the Python standard library. Needs internet.
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SERVER = "https://dataverse.harvard.edu"
DOI = "doi:10.7910/DVN/ODY7GH"
OUT = Path(__file__).resolve().parents[1] / "data" / "external" / "SignSpeakDataset.csv"
MIN_BYTES = 1_000_000  # the real file is about 9.8 MB


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "aiana-download/1.0"})
    return urllib.request.urlopen(req, timeout=timeout)


def pick_file(files):
    """files: the dataset's file list from the Dataverse API. Returns (file_id, name) or None."""
    best = None
    for f in files:
        name = (f.get("label") or f["dataFile"].get("filename") or "")
        low = name.lower()
        if "signspeak" in low and low.endswith((".csv", ".tab", ".tsv")):
            best = (f["dataFile"]["id"], name)
            if low.endswith(".csv"):
                break
    return best


def find_signspeak():
    url = f"{SERVER}/api/datasets/:persistentId/?persistentId={urllib.parse.quote(DOI)}"
    with get(url) as r:
        meta = json.load(r)
    return pick_file(meta["data"]["latestVersion"]["files"])


def download(file_id, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Dataverse converts uploaded CSVs to its own .tab; format=original asks for the file as uploaded.
    for suffix in ("?format=original", ""):
        try:
            with get(f"{SERVER}/api/access/datafile/{file_id}{suffix}", timeout=300) as r:
                data = r.read()
            if len(data) >= MIN_BYTES:
                dest.write_bytes(data)
                return len(data)
        except urllib.error.HTTPError:
            continue
    raise RuntimeError("download failed or file too small")


def check(path):
    """Quick sanity check with the standard library only: tab or comma separated, many columns."""
    import csv
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        head = f.readline()
        delim = "\t" if head.count("\t") > head.count(",") else ","
        cols = len(next(csv.reader([head], delimiter=delim)))
        rows = sum(1 for _ in f)
    print(f"  check: delimiter {'TAB' if delim == chr(9) else 'COMMA'}, {cols} columns, {rows} data rows")
    if cols < 50 or rows < 100:
        print("  WARNING: file looks wrong (expected ~397 columns, ~7200 rows). Run inspect_dataset.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    print("SignSpeak ->", OUT)
    if OUT.exists() and OUT.stat().st_size >= MIN_BYTES and not a.force:
        print("  already there, skipping (use --force to download again)")
        return
    try:
        found = find_signspeak()
        if not found:
            raise RuntimeError("could not find SignSpeakDataset in the dataset's file list")
        print(f"  downloading '{found[1]}' (file id {found[0]}) ...")
        size = download(found[0], OUT)
        print(f"  saved {size / 1e6:.1f} MB")
    except Exception as e:  # network down, API change, blocked site...
        print(f"  FAILED: {e}")
        print("  Manual fallback: open https://doi.org/10.7910/DVN/ODY7GH, download SignSpeakDataset.csv,")
        print(f"  and save it as {OUT}")
        sys.exit(1)
    try:
        check(OUT)
    except Exception as e:  # the check is only advice; the file is already saved
        print(f"  (could not check the file: {e})")
    print("Done. Next: python scripts/inspect_dataset.py data/external")


if __name__ == "__main__":
    main()