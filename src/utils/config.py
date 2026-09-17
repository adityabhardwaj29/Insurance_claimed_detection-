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
    CORS_ORIGINS: List[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "*").split(",")
            if origin.strip()
        ]
    )

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
