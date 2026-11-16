"""kNN / SVM / Random Forest baselines on summary features + confusion matrix.
Usage:
  python scripts/run_baselines.py                    (SignSpeak from data/external)
  python scripts/run_baselines.py --synthetic        (self-test with fake data, no download)
  python scripts/run_baselines.py --npz data/processed/own.npz
Uses leave-one-person-out if the data has more than one user, otherwise 5-fold stratified (and says so)."""
import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sklearn.ensemble import RandomForestClassifier  # noqa: E402
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score  # noqa: E402
from sklearn.model_selection import LeaveOneGroupOut, StratifiedKFold  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.svm import SVC  # noqa: E402

from aiana.preprocessing.signspeak import load_signspeak, per_user_minmax  # noqa: E402


def features(X):
    """(N,64,C) -> (N, 7*C): mean, std, min, max, first, last, slope per channel."""
    t = np.linspace(-1, 1, X.shape[1])[None, :, None]
    slope = (X * t).sum(1) / (t ** 2).sum()
    return np.concatenate([X.mean(1), X.std(1), X.min(1), X.max(1), X[:, 0], X[:, -1], slope], axis=1)


def synthetic(n_users=4, n_classes=6, reps=10, seed=0):
    rng = np.random.default_rng(seed)
    protos = rng.uniform(0.2, 0.8, (n_classes, 5))
    X, y, u = [], [], []
    for k in range(n_users):
        gain, off = rng.uniform(0.7, 1.3), rng.uniform(-0.1, 0.1)
        for c in range(n_classes):
            for _ in range(reps):
                tt = np.linspace(0, 1, 64)[:, None]
                X.append((protos[c] * (0.5 + 0.5 * np.sin(np.pi * tt)) * gain + off + rng.normal(0, 0.03, (64, 5))))
                y.append(f"g{c}"); u.append(f"user{k}")
    return np.array(X, np.float32), np.array(y), np.array(u)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz"); ap.add_argument("--root", default="data/external")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    if a.synthetic:
        X, y, u = synthetic()
    elif a.npz:
        d = np.load(a.npz, allow_pickle=True); X, y, u = d["X"], d["y"], d["user"]
    else:
        X, y, u = load_signspeak(a.root)
    X = per_user_minmax(X, u)
    F = features(X)
    classes = sorted(set(y))
    print(f"{len(y)} samples, {len(classes)} classes, {len(set(u))} users, X shape {X.shape}")
    if len(set(u)) > 1:
        splits, name = list(LeaveOneGroupOut().split(F, y, u)), "leave-one-person-out"
    else:
        splits, name = list(StratifiedKFold(5, shuffle=True, random_state=0).split(F, y)), "5-fold stratified (single/unknown user: NOT an unseen-person result)"
    print("Split:", name)
    models = {"kNN": KNeighborsClassifier(3), "SVM": SVC(C=10), "RandomForest": RandomForestClassifier(200, random_state=0)}
    Path(a.out).mkdir(exist_ok=True)
    for mname, m in models.items():
        pred = np.empty(len(y), dtype=y.dtype)
        for tr, te in splits:
            pipe = make_pipeline(StandardScaler(), m)
            pipe.fit(F[tr], y[tr]); pred[te] = pipe.predict(F[te])
        print(f"{mname:13s} accuracy {accuracy_score(y, pred):.3f}  macro-F1 {f1_score(y, pred, average='macro'):.3f}")
        cm = confusion_matrix(y, pred, labels=classes)
        np.savetxt(Path(a.out) / f"cm_{mname}.csv", cm, fmt="%d", delimiter=",", header=",".join(classes), comments="")
        try:
            import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(9, 8)); ax.imshow(cm, cmap="Blues")
            ax.set_xticks(range(len(classes)), classes, rotation=90, fontsize=6); ax.set_yticks(range(len(classes)), classes, fontsize=6)
            ax.set_xlabel("predicted"); ax.set_ylabel("true"); ax.set_title(f"{mname} - {name}", fontsize=8)
            fig.tight_layout(); fig.savefig(Path(a.out) / f"cm_{mname}.png", dpi=120); plt.close(fig)
        except Exception as e:  # plotting is optional
            print("  (no plot:", e, ")")
    print("Saved confusion matrices in", a.out)


if __name__ == "__main__":
    main()
