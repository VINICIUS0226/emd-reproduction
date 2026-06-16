from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
LOCAL_BASELINES = ROOT / "results" / "baselines"
OFFICIAL_RESULTS = ROOT / "external" / "EMD" / "results"
OUT = ROOT / "results" / "figures_llm_comparison"


COUNT_RE = re.compile(r"^\s*([0-9.]+)\s+\((\d+)/(\d+)\)\s*$")


def parse_score(value: str) -> tuple[float, int, int]:
    match = COUNT_RE.match(str(value))
    if not match:
        raise ValueError(f"Formato inesperado de resultado: {value!r}")
    return float(match.group(1)), int(match.group(2)), int(match.group(3))


def official_weighted_accuracy(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    rows = []
    for col in df.columns:
        if col == "Mutation Operators":
            continue
        correct = 0
        total = 0
        for value in df[col]:
            _, c, n = parse_score(value)
            correct += c
            total += n
        rows.append({"method": col, "accuracy": correct / total, "correct": correct, "total": total})
    return pd.DataFrame(rows).sort_values("accuracy", ascending=False)


def official_operator_long(path: Path, top_n: int = 10) -> pd.DataFrame:
    raw = pd.read_csv(path)
    den = raw.iloc[:, 1].map(lambda x: parse_score(x)[2])
    raw = raw.assign(total=den).sort_values("total", ascending=False).head(top_n)
    rows = []
    for _, row in raw.iterrows():
        op = row["Mutation Operators"]
        for col in raw.columns:
            if col in {"Mutation Operators", "total"}:
                continue
            pct, correct, total = parse_score(row[col])
            rows.append(
                {
                    "operator": op,
                    "method": col,
                    "accuracy": pct / 100.0,
                    "correct": correct,
                    "total": total,
                }
            )
    return pd.DataFrame(rows)


def local_baseline_accuracy() -> pd.DataFrame:
    summary = pd.read_csv(LOCAL_BASELINES / "summary.csv")
    name_map = {
        "logistic_regression": "Local Logistic Regression",
        "linear_svm": "Local Linear SVM",
        "random_forest": "Local Random Forest",
        "knn": "Local KNN",
    }
    summary["method"] = summary["model"].map(name_map)
    return summary[["method", "accuracy", "precision", "recall", "f1"]]


def save_bar(df: pd.DataFrame, path: Path, title: str, x_label: str = "Acuracia") -> None:
    fig, ax = plt.subplots(figsize=(9.4, max(4.2, 0.43 * len(df))))
    colors = ["#2F6F9F" if not m.startswith("Local") else "#D1495B" for m in df["method"]]
    bars = ax.barh(df["method"], df["accuracy"], color=colors)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_xlim(0, 1.02)
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.012, bar.get_y() + bar.get_height() / 2, f"{width:.3f}", va="center")
    fig.tight_layout()
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def save_heatmap(df: pd.DataFrame, path: Path, title: str) -> None:
    pivot = df.pivot(index="operator", columns="method", values="accuracy")
    fig, ax = plt.subplots(figsize=(11.6, 6.2))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".2f",
        cmap="YlGnBu",
        vmin=0,
        vmax=1,
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "Acuracia"},
        ax=ax,
    )
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel("Operador de mutacao")
    fig.tight_layout()
    fig.savefig(path.with_suffix(".png"), bbox_inches="tight")
    fig.savefig(path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.05)
    plt.rcParams.update({"savefig.dpi": 300, "figure.dpi": 160, "font.family": "DejaVu Sans"})

    llm = official_weighted_accuracy(OFFICIAL_RESULTS / "LLM_strategies_all_operators.csv")
    categories = official_weighted_accuracy(OFFICIAL_RESULTS / "EMD_categories_all_operators.csv")
    local = local_baseline_accuracy()

    save_bar(
        llm.sort_values("accuracy"),
        OUT / "official_llm_strategies_weighted_accuracy",
        "Resultados oficiais por estrategia LLM no pacote do artigo",
    )

    category_plus_local = pd.concat(
        [
            categories[["method", "accuracy"]],
            local[["method", "accuracy"]],
        ],
        ignore_index=True,
    ).sort_values("accuracy")
    save_bar(
        category_plus_local,
        OUT / "official_categories_vs_local_baselines_accuracy",
        "Comparacao: categorias oficiais do artigo e baselines locais reproduzidos",
    )

    llm_top = official_operator_long(OFFICIAL_RESULTS / "LLM_strategies_all_operators.csv", top_n=10)
    save_heatmap(
        llm_top,
        OUT / "official_llm_top10_operator_heatmap",
        "Resultados oficiais LLM por operador Top-10",
    )

    llm.to_csv(OUT / "official_llm_strategies_weighted_accuracy.csv", index=False)
    category_plus_local.to_csv(OUT / "official_categories_vs_local_baselines_accuracy.csv", index=False)

    notes = [
        "Comparacao gerada a partir dos CSVs oficiais do pacote do artigo e dos baselines locais reproduzidos.",
        "Os percentuais oficiais por operador foram agregados por media ponderada usando os contadores correto/total.",
        "Inferencia LLM real nao foi executada neste ambiente: nao ha torch/transformers/openai, chave OPENAI_API_KEY ou checkpoints locais.",
        "Comparacao local por operador nao foi gerada porque o pacote local disponivel nao inclui a coluna de operador nos pares/codigo.",
        f"Melhor estrategia LLM oficial agregada: {llm.iloc[0]['method']} = {llm.iloc[0]['accuracy']:.4f}.",
        f"Melhor baseline local por accuracy: {local.sort_values('accuracy', ascending=False).iloc[0]['method']} = {local.sort_values('accuracy', ascending=False).iloc[0]['accuracy']:.4f}.",
    ]
    (OUT / "comparison_notes.txt").write_text("\n".join(notes) + "\n", encoding="utf-8")
    print("\n".join(notes))
    print(f"Saidas salvas em: {OUT}")


if __name__ == "__main__":
    main()
