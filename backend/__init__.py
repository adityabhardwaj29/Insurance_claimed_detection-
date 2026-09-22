"""
backend
-------
FraudShield AI Enterprise Intelligence & Analytics Backend.
Unifies the production FastAPI REST API service with the core
machine learning, knowledge graph, and fraud scoring engines.

Usage:
    from backend import api, src
    from backend.main import app
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Expose api and src directly under backend namespace for clean modular access
import api as api
import src as src

__version__ = "1.0.0"
__all__ = ["api", "src", "app"]
