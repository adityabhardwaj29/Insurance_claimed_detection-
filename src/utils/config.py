"""
src/utils/config.py
-------------------
Environment and application configuration for the Fraud Detection system.
Does NOT hardcode database credentials. Reads from environment variables
with sensible defaults for local execution.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Settings:
    """Application settings read from environment variables."""
    ROOT: Path = ROOT

    # Database
    DATABASE_PATH: Path = field(
        default_factory=lambda: Path(
            os.getenv("DATABASE_PATH", str(ROOT / "database" / "fraud_detection.db"))
        )
    )
    DATABASE_URL: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", f"sqlite:///{ROOT}/database/fraud_detection.db"
        )
    )

    # CORS
    @staticmethod
    def _clean_cors_origins() -> List[str]:
        raw = os.getenv("CORS_ORIGINS", "*").strip()
        origins = []
        if raw and raw != "*":
            for item in raw.split(","):
                clean = item.strip().rstrip("/")
                if not clean:
                    continue
                if not clean.startswith("http://") and not clean.startswith("https://"):
                    origins.append(f"https://{clean}")
                    origins.append(f"http://{clean}")
                else:
                    origins.append(clean)
        # Always include production and local development origins
        for d in [
            "https://insurance-claimed-detection.vercel.app",
            "https://insurance-fraud-analytics.streamlit.app",
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8501",
        ]:
            if d not in origins:
                origins.append(d)
        return origins

    CORS_ORIGINS: List[str] = field(default_factory=_clean_cors_origins)

    # Models & Artifacts
    FRAUD_MODEL_PATH: Path = field(
        default_factory=lambda: Path(
            os.getenv("FRAUD_MODEL_PATH", str(ROOT / "models" / "fraud_model" / "model.joblib"))
        )
    )
    FRAUD_MODEL_META_PATH: Path = field(
        default_factory=lambda: Path(
            os.getenv("FRAUD_MODEL_META_PATH", str(ROOT / "models" / "fraud_model" / "metadata.json"))
        )
    )
    ANOMALY_MODEL_PATH: Path = field(
        default_factory=lambda: Path(
            os.getenv("ANOMALY_MODEL_PATH", str(ROOT / "models" / "anomaly_model" / "isolation_forest.joblib"))
        )
    )
    GRAPH_NODES_PATH: Path = field(
        default_factory=lambda: Path(
            os.getenv("GRAPH_NODES_PATH", str(ROOT / "data" / "graph" / "nodes.csv"))
        )
    )
    GRAPH_EDGES_PATH: Path = field(
        default_factory=lambda: Path(
            os.getenv("GRAPH_EDGES_PATH", str(ROOT / "data" / "graph" / "edges.csv"))
        )
    )
    RISK_SCORES_PATH: Path = field(
        default_factory=lambda: Path(
            os.getenv("RISK_SCORES_PATH", str(ROOT / "data" / "features" / "final_risk_scores.csv"))
        )
    )
    FINAL_FEATURES_PATH: Path = field(
        default_factory=lambda: Path(
            os.getenv("FINAL_FEATURES_PATH", str(ROOT / "data" / "features" / "final_claim_features.csv"))
        )
    )

    # API metadata
    API_TITLE: str = "Graph-Enhanced Insurance Claim Fraud Detection API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = (
        "REST API providing multi-signal fraud prediction, graph network analysis, "
        "evidence explanations, and human-in-the-loop investigation case management."
    )


settings = Settings()
