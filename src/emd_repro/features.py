from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer


def make_tfidf(analyzer: str = "char_wb", ngram_range: tuple[int, int] = (3, 5), max_features: int = 50000) -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer=analyzer,
        ngram_range=ngram_range,
        max_features=max_features,
        lowercase=False,
    )

