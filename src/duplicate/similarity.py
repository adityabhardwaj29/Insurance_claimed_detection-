def numeric_similarity(a, b, scale=1.0):
    return max(0.0, 1.0 - abs(a-b)/max(scale, 1e-9))
