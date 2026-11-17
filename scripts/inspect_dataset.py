"""Print the structure of a dataset folder so we can verify the loader. Paste the output to Claude.
Usage: python scripts/inspect_dataset.py data/external"""
import sys
from pathlib import Path

import pandas as pd

root = Path(sys.argv[1] if len(sys.argv) > 1 else "data/external")
for f in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in (".csv", ".tsv", ".txt")):
    print(f"\n=== {f.relative_to(root)}  ({f.stat().st_size / 1e6:.1f} MB)")
    df = pd.read_csv(f, sep=None, engine="python", nrows=2000)
    print("shape (first 2000 rows):", df.shape)
    print("first 8 columns:", list(df.columns[:8]), "| last 4:", list(df.columns[-4:]))
    nonnum = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    print("non-numeric columns:", nonnum[:5])
    print("NaN cells:", int(df.isna().sum().sum()), "| min/max of numeric:", df.select_dtypes("number").min().min(), df.select_dtypes("number").max().max())
    print(df.iloc[:2, :10].to_string())
    for c in (["word"] if "word" in df.columns else nonnum[:1]):
        print("label values:", df[c].nunique(), list(df[c].unique()[:40]))
