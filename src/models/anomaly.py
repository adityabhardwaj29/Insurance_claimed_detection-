from sklearn.ensemble import IsolationForest
def build_model():
    return IsolationForest(n_estimators=200, contamination=0.1, random_state=42)
