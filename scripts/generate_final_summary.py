from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final_summary"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []

    baseline_names = {
        "logistic_regression": "Logistic Regression",
        "linear_svm": "Linear SVM",
        "random_forest": "Random Forest",
        "knn": "KNN",
    }
    baselines = pd.read_csv(ROOT / "results" / "baselines" / "summary.csv")
    for _, row in baselines.iterrows():
        rows.append(
            {
                "method": baseline_names.get(row["model"], row["model"]),
                "source": "local_cpu",
                "accuracy": row["accuracy"],
                "precision": row["precision"],
                "recall": row["recall"],
                "f1": row["f1"],
                "metric_average": "binary",
            }
        )

    tce = load_json(ROOT / "results" / "deterministic" / "tce_proxy" / "metrics.json")
    rows.append(
        {
            "method": "TCE proxy",
            "source": "local_cpu",
            "accuracy": tce["accuracy"],
            "precision": tce["precision"],
            "recall": tce["recall"],
            "f1": tce["f1"],
            "metric_average": "binary",
        }
    )

    embedding = load_json(ROOT / "results" / "official_text_embedding_small" / "metrics.json")
    rows.append(
        {
            "method": "Text-Embedding-3-Small checkpoint",
            "source": "official_checkpoint_cpu",
            "accuracy": embedding["accuracy"],
            "precision": embedding["precision_binary"],
            "recall": embedding["recall_binary"],
            "f1": embedding["f1_binary"],
            "metric_average": "binary",
        }
    )
    rows.append(
        {
            "method": "Text-Embedding-3-Small checkpoint",
            "source": "official_checkpoint_cpu",
            "accuracy": embedding["accuracy"],
            "precision": embedding["precision_macro"],
            "recall": embedding["recall_macro"],
            "f1": embedding["f1_macro"],
            "metric_average": "macro",
        }
    )

    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "model_summary.csv", index=False)

    plot_df = summary[summary["metric_average"] == "binary"].copy()
    order = plot_df.sort_values("f1", ascending=False)["method"]
    long = plot_df.melt(
        id_vars=["method"],
        value_vars=["accuracy", "precision", "recall", "f1"],
        var_name="metric",
        value_name="value",
    )
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.05)
    fig, ax = plt.subplots(figsize=(10.4, 5.4))
    sns.barplot(data=long, x="method", y="value", hue="metric", order=order, ax=ax)
    ax.set_title("Resumo dos metodos executados localmente")
    ax.set_xlabel("")
    ax.set_ylabel("Pontuacao")
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis="x", rotation=25)
    ax.legend(title="", ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.02), frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "executed_methods_summary.png", dpi=300, bbox_inches="tight")
    fig.savefig(OUT / "executed_methods_summary.pdf", bbox_inches="tight")
    plt.close(fig)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
