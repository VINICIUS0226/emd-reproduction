from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from torch import nn
from torch.utils.data import DataLoader, Dataset


ROOT = Path(__file__).resolve().parents[1]


class RobertaClassificationHead(nn.Module):
    def __init__(self, hidden_size: int, hidden_dropout_prob: float, num_class: int = 2):
        super().__init__()
        self.dense = nn.Linear(hidden_size * 2, hidden_size, dtype=torch.float64)
        self.dropout = nn.Dropout(hidden_dropout_prob)
        self.out_proj = nn.Linear(hidden_size, num_class, dtype=torch.float64)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x1, x2):
        x = torch.cat((x1, x2), dim=1)
        x = self.dropout(x)
        x = self.dense(x)
        x = torch.tanh(x)
        x = self.dropout(x)
        x = self.out_proj(x)
        return self.softmax(x)


class PairEmbeddingDataset(Dataset):
    def __init__(self, embedding_file: Path, pair_file: Path, code_db_file: Path):
        self.pairs = pd.read_csv(pair_file)
        self.code_db = pd.read_csv(code_db_file)
        self.embeddings = np.load(embedding_file)
        self.embedding_dict = {
            code_id: self.embeddings[idx]
            for idx, code_id in enumerate(self.code_db["id"].tolist())
        }

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx: int):
        row = self.pairs.iloc[idx]
        return (
            self.embedding_dict[row["code_id_1"]],
            self.embedding_dict[row["code_id_2"]],
            int(row["label"]),
            int(row["id"]),
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=ROOT
        / "external"
        / "EMD"
        / "Text-Embedding-3-Small"
        / "saved_models"
        / "checkpoints"
        / "text-embedding-3-small.bin",
    )
    parser.add_argument(
        "--embeddings",
        type=Path,
        default=ROOT
        / "external"
        / "EMD"
        / "Text-Embedding-3-Small"
        / "saved_models"
        / "embeddings"
        / "text-embedding-3-small.npy",
    )
    parser.add_argument(
        "--code-db",
        type=Path,
        default=ROOT / "external" / "EMD" / "dataset" / "MutantBench_code_db_java.csv",
    )
    parser.add_argument(
        "--test",
        type=Path,
        default=ROOT / "external" / "EMD" / "dataset" / "Mutant_B_hierarchical.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results" / "official_text_embedding_small",
    )
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    dataset = PairEmbeddingDataset(args.embeddings, args.test, args.code_db)
    dataloader = DataLoader(dataset, batch_size=args.batch_size)

    input_dim = dataset[0][0].shape[0]
    model = RobertaClassificationHead(input_dim, 0.1, 2)
    model.load_state_dict(torch.load(args.checkpoint, map_location="cpu"))
    model.eval()

    y_true: list[int] = []
    y_pred: list[int] = []
    ids: list[int] = []
    scores: list[float] = []

    start = time.perf_counter()
    with torch.no_grad():
        for x1, x2, labels, batch_ids in dataloader:
            logits = model(x1, x2)
            prob_equivalent = logits[:, 1].cpu().numpy()
            pred = (prob_equivalent > 0.5).astype(int)
            y_true.extend(labels.cpu().numpy().astype(int).tolist())
            y_pred.extend(pred.tolist())
            ids.extend(batch_ids.cpu().numpy().astype(int).tolist())
            scores.extend(prob_equivalent.tolist())
    elapsed = time.perf_counter() - start

    precision_b, recall_b, f1_b, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    precision_m, recall_m, f1_m, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro", zero_division=0
    )
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_binary": float(precision_b),
        "recall_binary": float(recall_b),
        "f1_binary": float(f1_b),
        "precision_macro": float(precision_m),
        "recall_macro": float(recall_m),
        "f1_macro": float(f1_m),
        "threshold": 0.5,
        "elapsed_seconds": elapsed,
        "examples": len(y_true),
        "seconds_per_example": elapsed / max(len(y_true), 1),
    }

    pd.DataFrame(
        {
            "id": ids,
            "label": y_true,
            "prediction": y_pred,
            "score_equivalent": scores,
        }
    ).to_csv(args.out / "predictions.csv", index=False)
    pd.DataFrame(
        confusion_matrix(y_true, y_pred, labels=[0, 1]),
        index=["true_0", "true_1"],
        columns=["pred_0", "pred_1"],
    ).to_csv(args.out / "confusion_matrix.csv")
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
