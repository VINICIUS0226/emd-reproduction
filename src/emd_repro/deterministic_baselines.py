from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import pandas as pd

from .data import load_split
from .metrics import save_outputs


COMMENT_RE = re.compile(r"//.*?$|/\*.*?\*/", flags=re.MULTILINE | re.DOTALL)
SPACE_RE = re.compile(r"\s+")


def normalize_java_fragment(code: str) -> str:
    """Normalize superficial formatting while preserving token content."""
    code = COMMENT_RE.sub("", str(code))
    code = SPACE_RE.sub("", code)
    return code.strip()


def predict_tce_proxy(df: pd.DataFrame) -> list[int]:
    """Conservative deterministic proxy: equivalent only when normalized code matches."""
    left = df["code_1"].map(normalize_java_fragment)
    right = df["code_2"].map(normalize_java_fragment)
    return (left == right).astype(int).tolist()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    test_df = load_split(args.data, "test")

    start = time.perf_counter()
    pred = predict_tce_proxy(test_df)
    elapsed = time.perf_counter() - start

    metrics = save_outputs(
        args.out,
        "tce_proxy",
        test_df["id"],
        test_df["label"].astype(int),
        pred,
    )

    model_dir = args.out / "tce_proxy"
    run_info = {
        "method": "tce_proxy",
        "description": (
            "Conservative deterministic proxy for trivial equivalence: predicts "
            "equivalent only when the two Java method fragments are identical after "
            "comment and whitespace normalization."
        ),
        "elapsed_seconds": elapsed,
        "examples": int(len(test_df)),
        "seconds_per_example": elapsed / max(len(test_df), 1),
        "metrics": metrics,
    }
    (model_dir / "run_info.json").write_text(
        json.dumps(run_info, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(run_info, indent=2))


if __name__ == "__main__":
    main()
