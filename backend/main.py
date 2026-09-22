"""
backend/main.py
---------------
Direct entry point for the FraudShield AI FastAPI backend application.
Enables running the backend server with:
    python backend/main.py
    uvicorn backend.main:app --port 8000 --reload
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure workspace root is always on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the production FastAPI instance
from api.main import app

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  FraudShield AI - Enterprise FastAPI Backend Service")
    print("  Host: http://localhost:8000")
    print("  API Documentation: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
