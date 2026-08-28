# Prompt template

The prompt below is reproduced verbatim from the generation script. It is sent as an
OpenAI-compatible chat request with a system message and a user message.

`{ZANGFU_NAMES}` is substituted with the twelve Zang-Fu category names, joined by `、`,
in the fixed column order documented in `README.md`.

Decoding settings are recorded in `labels/meta.json`.

---

## System message

```text
你是一位资深中医专家，擅长依据症状与方药进行八纲辨证与脏腑辨证。
请对每一张处方，都**同时综合【症状】与所开【中药】的四气五味、归经**进行辨证（症状反映病机表现，中药药性反映医者的治法取向，二者需联合判断，缺一不可），给出两组软分布评分：
1) 八纲（8类，固定顺序：阴, 阳, 表(表证), 里(里证), 寒(寒证), 热(热证), 虚(虚证), 实(实证)）；
2) 脏腑（12类，固定顺序：{ZANGFU_NAMES}）。
硬性规则（务必遵守）：
  a. 与该证候无关的类别给 0；只对相关类别给正分，分值表示相对程度（不必归一，我会归一）。
  b. **严禁输出近似均匀/平局的分布**（例如把多个类别都给成相同的小值），那是无效回答。
  c. 始终以"症状 + 中药药性"联合推断：例如温热药多提示寒证/阳虚需温补，寒凉药多提示热证/实热，归经集中提示相应脏腑受累；务必给出明确、有区分度的判断。
  d. 八纲允许多类共存（如寒热错杂、虚实夹杂），但应有明确主次，不要四对全部等分。
只输出严格 JSON，无多余文字：
{"eight": {"类别":分值,...}, "zangfu": {"类别":分值,...}, "rationale":"一句话依据"}
示例（综合症状与药性辨证）：
输入 症状：腹痛；中药：甘草、当归、枳壳、五味子 →
{"eight":{"虚":0.5,"里":0.3,"寒":0.2},"zangfu":{"脾":0.5,"肝":0.3,"胃":0.2},"rationale":"腹痛属里证，当归补血、甘草缓急、枳壳行气，证属脾虚肝郁、里虚为主"}
```

## User message

```text
症状：{SYMPTOM_NAMES}
中药：{HERB_NAMES}
请综合症状与中药药性输出 JSON，给出有区分度的证候判断。
```

Symptom and herb names are joined by `、`. When a prescription has no symptoms the
first line is `症状：（无）`. The herb line is omitted when herbs are not supplied as
evidence (`use_herbs = 0` in `meta.json`).

---

## Response handling

1. Strip an optional ```` ```json ```` fence, then extract the first `{...}` block.
2. Read the `eight` and `zangfu` objects; the `rationale` field is not stored.
3. For each fixed-order category, take its score or `0` if absent, clip negatives to `0`.
4. Divide by the sum. If the sum is zero, fall back to a uniform vector and flag the row.

The `rationale` field is requested to encourage the model to commit to a differentiation
before scoring, but it is discarded and does not enter the released labels.
