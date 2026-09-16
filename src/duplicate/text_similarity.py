"""
src/duplicate/text_similarity.py
--------------------------------
Deterministic text similarity algorithms for insurance claim descriptions and text fields.

Provides:
  - levenshtein_similarity: Character-level edit distance ratio via difflib (deterministic)
  - token_similarity: Token-level Jaccard similarity (word sets)
  - tfidf_cosine_similarity: TF-IDF vectorization with cosine similarity
  - hybrid_text_similarity: Weighted combination of token + sequence similarity
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

from src.duplicate.similarity import jaccard_similarity


def _clean_and_tokenize(text: Any) -> tuple[str, set[str]]:
    """Clean string and produce normalized text + token set."""
    if text is None:
        return ("", set())
    s = str(text).strip().lower()
    if not s or s == "nan":
        return ("", set())
    # Strip punctuation and split on whitespace
    tokens = set(re.findall(r"\b[a-z0-9]+\b", s))
    clean_str = " ".join(re.findall(r"\b[a-z0-9]+\b", s))
    return (clean_str, tokens)


def levenshtein_similarity(text_a: Any, text_b: Any) -> float:
    """
    Computes sequence similarity ratio in [0.0, 1.0] using difflib.SequenceMatcher.
    Deterministic, standard library, and robust to minor typos/formatting differences.
    """
    s_a, _ = _clean_and_tokenize(text_a)
    s_b, _ = _clean_and_tokenize(text_b)
    if not s_a and not s_b:
        return 1.0
    if not s_a or not s_b:
        return 0.0
    if s_a == s_b:
        return 1.0
    matcher = SequenceMatcher(None, s_a, s_b)
    return round(float(matcher.ratio()), 4)


def token_similarity(text_a: Any, text_b: Any) -> float:
    """
    Computes Jaccard similarity of word tokens between two texts in [0.0, 1.0].
    """
    _, tokens_a = _clean_and_tokenize(text_a)
    _, tokens_b = _clean_and_tokenize(text_b)
    return round(jaccard_similarity(tokens_a, tokens_b), 4)


def tfidf_cosine_similarity(text_a: Any, text_b: Any) -> float:
    """
    Computes TF-IDF cosine similarity between two text snippets in [0.0, 1.0].
    If vocabulary size is insufficient or texts are empty, falls back to token_similarity.
    """
    s_a, tokens_a = _clean_and_tokenize(text_a)
    s_b, tokens_b = _clean_and_tokenize(text_b)
    if not s_a and not s_b:
        return 1.0
    if not s_a or not s_b:
        return 0.0
    if s_a == s_b:
        return 1.0

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vec = TfidfVectorizer()
        matrix = vec.fit_transform([s_a, s_b])
        cos = cosine_similarity(matrix[0:1], matrix[1:2])[0, 0]
        return round(float(cos), 4)
    except Exception:
        # Fallback to token similarity if vectorizer cannot fit (e.g. single character tokens)
        return token_similarity(text_a, text_b)


def hybrid_text_similarity(
    text_a: Any,
    text_b: Any,
    token_weight: float = 0.5,
    seq_weight: float = 0.5,
) -> float:
    """
    Combines token Jaccard and character SequenceMatcher for robust string comparison.
    """
    tok = token_similarity(text_a, text_b)
    seq = levenshtein_similarity(text_a, text_b)
    tot = token_weight + seq_weight
    if tot <= 0:
        return 0.0
    return round((tok * token_weight + seq * seq_weight) / tot, 4)
