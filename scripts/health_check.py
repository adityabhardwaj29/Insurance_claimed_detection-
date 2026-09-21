"""
scripts/health_check.py
-----------------------
System Health & Integrity Verification Script for FraudShield AI.
Checks:
  1. Python runtime (>= 3.10)
  2. Core backend package imports (FastAPI, Pydantic, Uvicorn, Pandas, Scikit-learn, XGBoost, NetworkX)
  3. Configuration loading
  4. Database connectivity (Supabase PostgreSQL / SQLite fallback)
  5. Machine learning & anomaly model artifacts on disk
  6. Graph dataset files (nodes.csv, edges.csv)
  7. Critical directory structure

Returns exit code 0 if all essential systems are operational, non-zero on failure.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def check_python_version() -> bool:
    v = sys.version_info
    print(f"[*] Python version: {v.major}.{v.minor}.{v.micro}", end=" ... ")
    if v.major >= 3 and v.minor >= 10:
        print("[OK]")
        return True
    print("[FAIL] Requires Python 3.10+")
    return False


def check_dependencies() -> bool:
    print("[*] Core library dependencies", end=" ... ")
    required_pkgs = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "pandas",
        "numpy",
        "sklearn",
        "xgboost",
        "networkx",
        "joblib",
    ]
    missing = []
    for pkg in required_pkgs:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if not missing:
        print("[OK]")
        return True
    print(f"[FAIL] Missing: {', '.join(missing)}")
    return False


def check_configuration() -> bool:
    print("[*] System configuration loading", end=" ... ")
    try:
        from src.utils.config import settings
        _ = settings.API_TITLE
        print("[OK]")
        return True
    except Exception as e:
        print(f"[FAIL] Config error: {e}")
        return False


def check_database() -> bool:
    print("[*] Database connectivity", end=" ... ")
    try:
        from api.db import db
        res = db.query_one("SELECT COUNT(*) as c FROM claims")
        count = res["c"] if res else 0
        print(f"[OK] ({db.engine_type}, {count} claims recorded)")
        return True
    except Exception as e:
        print(f"[FAIL] Database error: {e}")
        return False


def check_ml_models() -> bool:
    print("[*] Machine learning model artifacts", end=" ... ")
    required_models = [
        ROOT / "models" / "fraud_model" / "model.joblib",
        ROOT / "models" / "anomaly_model" / "isolation_forest.joblib",
        ROOT / "models" / "graph_enhanced_model" / "model.joblib",
    ]
    missing = [str(p.name) for p in required_models if not p.exists()]
    if not missing:
        print("[OK]")
        return True
    print(f"[FAIL] Missing model artifacts: {', '.join(missing)}")
    return False


def check_graph_data() -> bool:
    print("[*] Graph network datasets", end=" ... ")
    nodes = ROOT / "data" / "graph" / "nodes.csv"
    edges = ROOT / "data" / "graph" / "edges.csv"
    if nodes.exists() and edges.exists():
        print(f"[OK] ({nodes.stat().st_size // 1024} KB nodes, {edges.stat().st_size // 1024} KB edges)")
        return True
    print(f"[FAIL] Missing graph files in {ROOT / 'data' / 'graph'}")
    return False


def check_directories() -> bool:
    print("[*] Runtime directory structure", end=" ... ")
    required_dirs = [
        ROOT / "logs",
        ROOT / "data" / "raw",
        ROOT / "data" / "processed",
        ROOT / "data" / "features",
        ROOT / "data" / "graph",
    ]
    for d in required_dirs:
        d.mkdir(parents=True, exist_ok=True)
    print("[OK]")
    return True


def main() -> int:
    print("=" * 60)
    print("  FraudShield AI - System Health & Diagnostic Suite")
    print("=" * 60)

    checks = [
        check_python_version(),
        check_directories(),
        check_dependencies(),
        check_configuration(),
        check_database(),
        check_ml_models(),
        check_graph_data(),
    ]

    print("=" * 60)
    if all(checks):
        print("  [SUCCESS] All system health checks passed.")
        print("=" * 60)
        return 0
    else:
        print("  [WARNING] Some system checks failed. Review output above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
