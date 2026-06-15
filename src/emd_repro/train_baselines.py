from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from .data import load_split, pair_text
from .features import make_tfidf
from .metrics import save_outputs


def build_model(name: str, random_state: int):
    if name == "logistic_regression":
        return LogisticRegression(max_iter=2000, class_weight="balanced", random_state=random_state)
    if name == "linear_svm":
        return LinearSVC(class_weight="balanced", random_state=random_state)
    if name == "random_forest":
        return RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )
    if name == "knn":
        return KNeighborsClassifier(n_neighbors=5)
    raise ValueError(f"Modelo desconhecido: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/baseline.yaml"))
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    random_state = int(config.get("random_state", 42))
    feature_cfg = config.get("features", {})

    train_df = load_split(args.data, "train")
    test_df = load_split(args.data, "test")

    x_train = pair_text(train_df)
    y_train = train_df["label"].astype(int)
    x_test = pair_text(test_df)
    y_test = test_df["label"].astype(int)

    rows = []
    args.out.mkdir(parents=True, exist_ok=True)

    for model_name in config["models"]:
        ngram_range = tuple(feature_cfg.get("ngram_range", [3, 5]))
        pipeline = Pipeline(
            steps=[
                (
                    "tfidf",
                    make_tfidf(
                        analyzer=feature_cfg.get("analyzer", "char_wb"),
                        ngram_range=ngram_range,
                        max_features=int(feature_cfg.get("max_features", 50000)),
                    ),
                ),
                ("clf", build_model(model_name, random_state)),
            ]
        )
        pipeline.fit(x_train, y_train)
        pred = pipeline.predict(x_test)
        metrics = save_outputs(args.out, model_name, test_df["id"], y_test, pred)
        joblib.dump(pipeline, args.out / model_name / "model.joblib")
        rows.append({"model": model_name, **metrics})
        print(model_name, metrics)

    pd.DataFrame(rows).sort_values("f1", ascending=False).to_csv(
        args.out / "summary.csv", index=False
    )


if __name__ == "__main__":
    main()

