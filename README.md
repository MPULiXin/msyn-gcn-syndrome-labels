# MSyn-GCN — LLM-generated weak syndrome labels

Weak Eight-Principles (八纲) and Zang-Fu (脏腑) syndrome labels for the public TCM
prescription dataset of Jin et al. (2020), generated with a large language model and
used as the supervision target for the diagnostic heads of MSyn-GCN.

This repository contains **only the labels and the prompt used to produce them**.
The model implementation is part of an ongoing project and is available from the
corresponding author on reasonable request.

---

## 1. What is in here

```
labels/
  eight_train.npy     (20625, 8)   float32   Eight-Principles distribution per prescription
  zangfu_train.npy    (20625, 12)  float32   Zang-Fu distribution per prescription
  eight_val.npy       ( 2292, 8)   float32
  zangfu_val.npy      ( 2292, 12)  float32
  eight_test.npy      ( 3443, 8)   float32
  zangfu_test.npy     ( 3443, 12)  float32
  meta.json                        column order and summary statistics
  split_indices.json               the validation row indices used
labels_preview.csv                 human-readable sample: symptoms, herbs, top category
prompt_template.md                 the exact prompt sent to the model
split_labels.py                    helper: reproduce the split from the original release
```

The underlying prescriptions are **not** redistributed here. Obtain `train.txt` and
`test.txt` from the original release by Jin et al. (2020).

---

## 2. Row alignment — read this first

The released arrays are already aligned with the three splits used in the paper:

| file | rows | aligned with |
|---|---|---|
| `eight_train.npy`, `zangfu_train.npy` | 20,625 | the training split |
| `eight_val.npy`, `zangfu_val.npy` | 2,292 | the validation split |
| `eight_test.npy`, `zangfu_test.npy` | 3,443 | `test.txt` of Jin et al. (2020), unchanged |

Alignment is **by line order**: row *i* of a label array corresponds to line *i*
(0-indexed) of the matching prescription file. There is no key column.

The training and validation splits were obtained by holding out 10% of the 22,917
prescriptions in the original `train.txt`, drawn uniformly at random at the
prescription level with seed 42. `split_indices.json` records the exact validation
row indices against the original file, and `split_labels.py` reproduces both the
prescription files and the label arrays from the original release. If you re-split
the data yourself, apply the identical index operation to the label arrays, otherwise
the supervision signal is silently mismatched.

## 3. Column order

### Eight Principles — 8 columns, fixed order

| idx | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|-----|---|---|---|---|---|---|---|---|
| 中文 | 阴 | 阳 | 表 | 里 | 寒 | 热 | 虚 | 实 |
| English | Yin | Yang | Exterior | Interior | Cold | Heat | Deficiency | Excess |

### Zang-Fu — 12 columns, fixed order

The order follows the twelve-meridian sequence used by the herb property table, so that
the label vector aligns with the model's Zang-Fu head.

| idx | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|-----|---|---|---|---|---|---|---|---|---|---|----|----|
| 中文 | 肺 | 心包 | 心 | 大肠 | 三焦 | 小肠 | 胃 | 胆 | 膀胱 | 脾 | 肝 | 肾 |
| English | Lung | Pericardium | Heart | Large Intestine | Triple Burner | Small Intestine | Stomach | Gallbladder | Bladder | Spleen | Liver | Kidney |

The same order is stored in `labels/meta.json` under `zangfu_names`.

---

## 4. How the labels were produced

For each prescription the model received the **symptom names and the prescribed herb
names**, and was asked to perform joint Eight-Principles and Zang-Fu differentiation,
reasoning from both the symptom presentation and the Four Qi, Five Flavors and
meridian tropism of the herbs. It returned a score for each relevant category and
zero for categories judged clinically irrelevant. See `prompt_template.md` for the
verbatim prompt.

Each response was parsed into a fixed-order vector, clipped at zero and renormalized
to sum to one. Identical (symptom set, herb set) inputs were labelled once and reused,
so the number of API calls is smaller than the number of prescriptions.

Generation settings are recorded in `meta.json` (`model`, `use_herbs`). Prescriptions
were labelled with herbs included as auxiliary evidence; the labels are therefore a
**training-time target only**, and the model that consumes them never sees herbs at
inference.

### Uniform fallbacks

Two situations produce a uniform vector rather than a sparse one: the response could
not be parsed or scored every category zero, or the input key was missing from the
response cache. In the released labels this is negligible — one Zang-Fu row in the
training split and none elsewhere — but the counts are recorded in `meta.json` as
`<split>_uniform_rows_eight` and `<split>_uniform_rows_zangfu`.

Average number of active dimensions (threshold `1e-4`):

| split | Eight-Principles | Zang-Fu |
|---|---|---|
| train | 3.82 | 3.95 |
| validation | 3.80 | 3.95 |
| test | 3.84 | 3.92 |

## 5. Quick check

```python
import numpy as np, json
E = np.load("labels/eight_train.npy")   # 20,625 rows
Z = np.load("labels/zangfu_train.npy")
meta = json.load(open("labels/meta.json"))

print(E.shape, Z.shape)                       # (N, 8) (N, 12)
print(np.allclose(E.sum(1), 1), np.allclose(Z.sum(1), 1))
print("avg active eight :", (E > 1e-4).sum(1).mean())
print("avg active zangfu:", (Z > 1e-4).sum(1).mean())
print("uniform rows     :", int(np.isclose(E, 1/8).all(1).sum()))
```

An activation threshold of `1e-4` is used throughout the paper when counting active
dimensions.

---

## 6. Citation

<!-- TODO: 论文接收后补上正式引用 -->

If you use these labels, please cite the paper and the original dataset:

- Li X, Luo W. MSyn-GCN: LLM weak supervision yields clinically readable syndrome
  representations for herb recommendation. *(under review)*
- Jin Y, et al. Syndrome-aware herb recommendation with multi-graph convolution
  network. ICDE 2020.

## 7. License

<!-- TODO: 选择许可证。数据类仓库常用 CC BY 4.0；若同时含代码，可对 split_labels.py 单独用 MIT。 -->
