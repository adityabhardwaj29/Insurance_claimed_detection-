from src.models.anomaly.models import build_isolation_forest
from src.models.anomaly.anomaly_detector import AnomalyDetector

def build_model():
    return build_isolation_forest(contamination=0.10, n_estimators=200, random_state=42)
