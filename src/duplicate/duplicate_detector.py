def duplicate_score(features):
    cols=[c for c in features if c.endswith("_similarity")]
    return float(features[cols].mean()) if cols else 0.0
