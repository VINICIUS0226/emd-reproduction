from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def find_csv(root: Path, include: list[str], exclude: list[str] | None = None) -> Path:
    exclude = exclude or []
    candidates = []
    for path in root.rglob("*.csv"):
        name = path.name.lower()
        if all(token.lower() in name for token in include) and not any(
            token.lower() in name for token in exclude
        ):
            candidates.append(path)
    if not candidates:
        raise FileNotFoundError(
            f"Nenhum CSV encontrado em {root} contendo {include} e excluindo {exclude}"
        )
    return sorted(candidates, key=lambda p: len(str(p)))[0]


def normalize_pairs(pairs: pd.DataFrame, code_db: pd.DataFrame) -> pd.DataFrame:
    required_pairs = {"id", "code_id_1", "code_id_2", "label"}
    required_code = {"id", "code"}

    missing_pairs = required_pairs - set(pairs.columns)
    missing_code = required_code - set(code_db.columns)
    if missing_pairs:
        raise ValueError(f"Colunas ausentes no arquivo de pares: {sorted(missing_pairs)}")
    if missing_code:
        raise ValueError(f"Colunas ausentes no code_db: {sorted(missing_code)}")

    code_lookup = code_db[["id", "code"]].rename(columns={"id": "code_id_1", "code": "code_1"})
    merged = pairs.merge(code_lookup, on="code_id_1", how="left")

    code_lookup = code_db[["id", "code"]].rename(columns={"id": "code_id_2", "code": "code_2"})
    merged = merged.merge(code_lookup, on="code_id_2", how="left")

    if merged[["code_1", "code_2"]].isna().any().any():
        missing = merged[merged[["code_1", "code_2"]].isna().any(axis=1)]
        raise ValueError(f"Ha pares com codigo nao encontrado. Exemplo de ids: {missing.head().to_dict('records')}")

    cols = ["id", "code_id_1", "code_id_2", "code_1", "code_2", "label"]
    if "operator" in code_db.columns:
        op_lookup = code_db[["id", "operator"]].rename(
            columns={"id": "code_id_2", "operator": "operator_2"}
        )
        merged = merged.merge(op_lookup, on="code_id_2", how="left")
        cols.append("operator_2")

    return merged[cols]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    dataset_root = args.author_repo / "dataset"
    if not dataset_root.exists():
        raise FileNotFoundError(f"Pasta dataset nao encontrada: {dataset_root}")

    code_db_path = find_csv(dataset_root, ["code", "db"])
    train_path = find_csv(dataset_root, ["train"])
    test_path = find_csv(dataset_root, ["test"])

    code_db = pd.read_csv(code_db_path)
    train_pairs = pd.read_csv(train_path)
    test_pairs = pd.read_csv(test_path)

    args.out.mkdir(parents=True, exist_ok=True)
    normalize_pairs(train_pairs, code_db).to_csv(args.out / "train.csv", index=False)
    normalize_pairs(test_pairs, code_db).to_csv(args.out / "test.csv", index=False)

    print(f"code_db: {code_db_path}")
    print(f"train:   {train_path}")
    print(f"test:    {test_path}")
    print(f"saida:   {args.out}")


if __name__ == "__main__":
    main()

