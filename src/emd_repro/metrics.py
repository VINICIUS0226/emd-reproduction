from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


def classification_report_dict(y_true, y_pred) -> dict[str, float]:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", zero_division=0
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def save_outputs(out_dir: Path, model_name: str, ids, y_true, y_pred) -> dict[str, float]:
    model_dir = out_dir / model_name
    model_dir.mkdir(parents=True, exist_ok=True)

    metrics = classification_report_dict(y_true, y_pred)
    (model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    predictions = pd.DataFrame({"id": ids, "label": y_true, "prediction": y_pred})
    predictions.to_csv(model_dir / "predictions.csv", index=False)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    pd.DataFrame(cm, index=["true_0", "true_1"], columns=["pred_0", "pred_1"]).to_csv(
        model_dir / "confusion_matrix.csv"
    )
    return metrics

