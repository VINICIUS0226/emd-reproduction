from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_split(data_dir: Path, split: str) -> pd.DataFrame:
    path = data_dir / f"{split}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
    df = pd.read_csv(path)
    required = {"id", "code_1", "code_2", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colunas ausentes em {path}: {sorted(missing)}")
    return df


def pair_text(df: pd.DataFrame) -> pd.Series:
    return (
        "CODE_A:\n"
        + df["code_1"].fillna("")
        + "\n\nCODE_B:\n"
        + df["code_2"].fillna("")
    )

