from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


ROOT = Path(__file__).resolve().parents[1]

PROMPT_TEMPLATE = """You are evaluating equivalent mutant detection for Java methods.

Decide whether the mutant method is semantically equivalent to the original method.

Return only one JSON object with this schema:
{{"label": 0 or 1, "confidence": "low|medium|high", "rationale": "short reason"}}

Use label 1 if the mutant is equivalent and label 0 if it is not equivalent.

Original Java method:
```java
{code_1}
```

Mutant Java method:
```java
{code_2}
```
"""


def stratified_sample(df: pd.DataFrame, sample_size: int, seed: int) -> pd.DataFrame:
    per_class = max(sample_size // 2, 1)
    sampled = []
    for label, group in df.groupby("label", sort=True):
        n = min(per_class, len(group))
        sampled.append(group.sample(n=n, random_state=seed))
    sample = pd.concat(sampled).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    if len(sample) < sample_size:
        remaining = df.drop(index=sample.index, errors="ignore")
        extra_n = min(sample_size - len(sample), len(remaining))
        if extra_n:
            sample = pd.concat(
                [sample, remaining.sample(n=extra_n, random_state=seed)],
                ignore_index=True,
            )
    return sample.head(sample_size)


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return {"label": None, "confidence": None, "rationale": text.strip()}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"label": None, "confidence": None, "rationale": text.strip()}


def estimate_cost(usage, input_cost_per_1m: float | None, output_cost_per_1m: float | None) -> float | None:
    if input_cost_per_1m is None or output_cost_per_1m is None or usage is None:
        return None
    input_tokens = getattr(usage, "input_tokens", None) or 0
    output_tokens = getattr(usage, "output_tokens", None) or 0
    return (input_tokens / 1_000_000) * input_cost_per_1m + (
        output_tokens / 1_000_000
    ) * output_cost_per_1m


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "processed" / "test.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "openai_stratified_sample")
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5.5"))
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-output-tokens", type=int, default=180)
    parser.add_argument("--input-cost-per-1m", type=float, default=None)
    parser.add_argument("--output-cost-per-1m", type=float, default=None)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.data)
    sample = stratified_sample(df, args.sample_size, args.seed)
    sample[["id", "code_id_1", "code_id_2", "label"]].to_csv(args.out / "sample.csv", index=False)
    (args.out / "prompt_template.txt").write_text(PROMPT_TEMPLATE, encoding="utf-8")

    run_info = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "temperature": args.temperature,
        "max_output_tokens": args.max_output_tokens,
        "sample_size_requested": args.sample_size,
        "sample_size_actual": int(len(sample)),
        "seed": args.seed,
        "data": str(args.data),
        "status": "initialized",
    }

    if not os.environ.get("OPENAI_API_KEY"):
        run_info["status"] = "skipped_no_api_key"
        (args.out / "run_info.json").write_text(json.dumps(run_info, indent=2), encoding="utf-8")
        print(json.dumps(run_info, indent=2))
        return

    from openai import OpenAI

    client = OpenAI()
    rows = []
    total_cost = 0.0
    any_cost = False
    start_all = time.perf_counter()
    for _, row in sample.iterrows():
        prompt = PROMPT_TEMPLATE.format(code_1=row["code_1"], code_2=row["code_2"])
        start = time.perf_counter()
        response = client.responses.create(
            model=args.model,
            input=prompt,
            temperature=args.temperature,
            max_output_tokens=args.max_output_tokens,
        )
        elapsed = time.perf_counter() - start
        text = response.output_text
        parsed = extract_json(text)
        usage = getattr(response, "usage", None)
        cost = estimate_cost(usage, args.input_cost_per_1m, args.output_cost_per_1m)
        if cost is not None:
            total_cost += cost
            any_cost = True
        rows.append(
            {
                "id": row["id"],
                "label": int(row["label"]),
                "prediction": parsed.get("label"),
                "confidence": parsed.get("confidence"),
                "rationale": parsed.get("rationale"),
                "raw_response": text,
                "elapsed_seconds": elapsed,
                "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
                "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
                "estimated_cost_usd": cost,
            }
        )

    pred_df = pd.DataFrame(rows)
    pred_df.to_csv(args.out / "predictions.csv", index=False)
    valid = pred_df[pred_df["prediction"].isin([0, 1])].copy()
    if not valid.empty:
        y_true = valid["label"].astype(int)
        y_pred = valid["prediction"].astype(int)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "valid_predictions": int(len(valid)),
        }
        pd.DataFrame(
            confusion_matrix(y_true, y_pred, labels=[0, 1]),
            index=["true_0", "true_1"],
            columns=["pred_0", "pred_1"],
        ).to_csv(args.out / "confusion_matrix.csv")
        (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    else:
        metrics = {"valid_predictions": 0}

    run_info.update(
        {
            "status": "completed",
            "elapsed_seconds": time.perf_counter() - start_all,
            "metrics": metrics,
            "estimated_cost_usd": total_cost if any_cost else None,
        }
    )
    (args.out / "run_info.json").write_text(json.dumps(run_info, indent=2), encoding="utf-8")
    print(json.dumps(run_info, indent=2))


if __name__ == "__main__":
    main()
