# -*- coding: utf-8 -*-
"""
split_labels.py — derive validation-split label files from the released labels.

The released labels are aligned by line order with the ORIGINAL train.txt
(N = 22,917). The study holds out 10% of those prescriptions as a validation split.
This script applies the identical index operation to the label arrays, so that
labels and prescriptions stay aligned.

Run it from the repository root with the original train.txt available:

    python split_labels.py --train_txt /path/to/train.txt --out_dir labels_split

Outputs
    labels_split/train_A.txt, val_A.txt          prescriptions
    labels_split/eight_train_A.npy, ...          labels for each split
    labels_split/split_indices.json              the exact row indices used

Any change to --seed or --val_frac produces a different split; the study used the
defaults below.
"""

import argparse
import json
import os
import random

import numpy as np

SEED = 42
VAL_FRAC = 0.10


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--train_txt", required=True,
                   help="original train.txt from Jin et al. (2020)")
    p.add_argument("--labels_dir", default="labels")
    p.add_argument("--out_dir", default="labels_split")
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--val_frac", type=float, default=VAL_FRAC)
    return p.parse_args()


def main():
    a = parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    with open(a.train_txt, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    n = len(lines)

    E = np.load(os.path.join(a.labels_dir, "eight_train.npy"))
    Z = np.load(os.path.join(a.labels_dir, "zangfu_train.npy"))
    if not (len(E) == len(Z) == n):
        raise SystemExit(
            f"row count mismatch: train.txt has {n} lines, "
            f"eight_train.npy has {len(E)}, zangfu_train.npy has {len(Z)}. "
            "The labels must be aligned line-by-line with this exact train.txt."
        )

    rnd = random.Random(a.seed)
    idx = list(range(n))
    rnd.shuffle(idx)
    n_val = round(n * a.val_frac)
    val_idx = sorted(idx[:n_val])
    val_set = set(val_idx)
    tr_idx = [i for i in range(n) if i not in val_set]

    for name, rows in (("train_A", tr_idx), ("val_A", val_idx)):
        with open(os.path.join(a.out_dir, name + ".txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines[i] for i in rows) + "\n")
        np.save(os.path.join(a.out_dir, f"eight_{name}.npy"), E[rows])
        np.save(os.path.join(a.out_dir, f"zangfu_{name}.npy"), Z[rows])
        print(f"{name}: {len(rows)} rows")

    with open(os.path.join(a.out_dir, "split_indices.json"), "w") as f:
        json.dump({"seed": a.seed, "val_frac": a.val_frac,
                   "n_total": n, "val_indices": val_idx}, f)
    print("wrote", os.path.abspath(a.out_dir))


if __name__ == "__main__":
    main()
