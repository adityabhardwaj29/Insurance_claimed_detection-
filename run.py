"""
run.py
------
One-Command Operational Entry Point & Startup CLI for Graph-Enhanced Insurance Fraud Detection.

Usage:
    python run.py --all          # Launch both FastAPI Backend and Streamlit Dashboard concurrently
    python run.py --api          # Launch FastAPI backend service on port 8000
    python run.py --dashboard    # Launch Streamlit interactive dashboard on port 8501
    python run.py --pipeline     # Execute reproducible end-to-end data/feature/model/case pipeline
    python run.py --journey CID  # Trace and verify complete claim journey for a specific claim ID
    python run.py --test         # Execute full pytest automated test suite
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


# Configure standard streams for UTF-8 on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_pipeline() -> None:
    """Executes the full end-to-end analytical pipeline."""
    from src.pipeline import run_full_pipeline
    print("\nStarting full end-to-end pipeline execution...")
    run_full_pipeline(rebuild_db=False, verbose=True)


def run_journey(claim_id: str) -> None:
    """Traces and verifies the end-to-end claim journey."""
    from src.pipeline import verify_claim_journey
    verify_claim_journey(claim_id=claim_id, verbose=True)


def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    """Launches the production FastAPI server using Uvicorn."""
    import uvicorn
    print(f"\n[API] Launching FastAPI Backend on http://{host}:{port} (Swagger docs: http://localhost:{port}/docs)")
    uvicorn.run("api.main:app", host=host, port=port, reload=reload)


def run_dashboard(port: int = 8501) -> None:
    """Launches the Streamlit Fraud Analytics Dashboard."""
    dashboard_app = ROOT / "dashboard" / "app.py"
    cmd = [sys.executable, "-m", "streamlit", "run", str(dashboard_app), "--server.port", str(port)]
    print(f"\n[DASHBOARD] Launching Streamlit Dashboard on http://localhost:{port}")
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nStreamlit dashboard terminated.")


def run_tests() -> None:
    """Runs the full repository automated test suite."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    print("\n[TESTS] Running full automated test suite...")
    subprocess.run(cmd)


def run_all(api_port: int = 8000, dash_port: int = 8501) -> None:
    """
    Launches both FastAPI backend and Streamlit dashboard concurrently.
    Monitors processes and handles clean shutdown.
    """
    import subprocess
    print("=" * 70)
    print("STARTING GRAPH-ENHANCED INSURANCE FRAUD PLATFORM (API + DASHBOARD)")
    print("=" * 70)

    # 1. Start FastAPI in background process
    api_cmd = [
        sys.executable, "-m", "uvicorn", "api.main:app",
        "--host", "0.0.0.0", "--port", str(api_port)
    ]
    api_proc = subprocess.Popen(api_cmd, cwd=str(ROOT))
    print(f"[API] FastAPI server started (PID: {api_proc.pid}) -> http://localhost:{api_port}/docs")

    time.sleep(2)  # Allow API to bind

    # 2. Start Streamlit in foreground
    dash_app = ROOT / "dashboard" / "app.py"
    dash_cmd = [
        sys.executable, "-m", "streamlit", "run", str(dash_app),
        "--server.port", str(dash_port)
    ]
    print(f"[DASHBOARD] Streamlit Dashboard launching -> http://localhost:{dash_port}")
    print("Press Ctrl+C to terminate both services.\n")

    try:
        dash_proc = subprocess.Popen(dash_cmd, cwd=str(ROOT))
        dash_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down platform services...")
    finally:
        api_proc.terminate()
        try:
            api_proc.wait(timeout=5)
        except Exception:
            api_proc.kill()
        print("All platform services stopped cleanly.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Graph-Enhanced Insurance Claim Fraud Detection - Master CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Launch both FastAPI and Streamlit concurrently")
    group.add_argument("--api", action="store_true", help="Launch FastAPI backend on port 8000")
    group.add_argument("--dashboard", action="store_true", help="Launch Streamlit dashboard on port 8501")
    group.add_argument("--pipeline", action="store_true", help="Run full reproducible pipeline from scratch")
    group.add_argument("--journey", type=str, nargs="?", const="CLM00001", help="Verify single claim journey (default: CLM00001)")
    group.add_argument("--test", action="store_true", help="Run automated test suite")

    parser.add_argument("--api-port", type=int, default=8000, help="Port for FastAPI server (default: 8000)")
    parser.add_argument("--dash-port", type=int, default=8501, help="Port for Streamlit dashboard (default: 8501)")

    args = parser.parse_args()

    if args.all:
        run_all(api_port=args.api_port, dash_port=args.dash_port)
    elif args.api:
        run_api(port=args.api_port)
    elif args.dashboard:
        run_dashboard(port=args.dash_port)
    elif args.pipeline:
        run_pipeline()
    elif args.journey:
        run_journey(args.journey)
    elif args.test:
        run_tests()
    else:
        # Default behavior: print help and system status summary
        print("=" * 70)
        print("GRAPH-ENHANCED INSURANCE FRAUD DETECTION PLATFORM")
        print("=" * 70)
        print("Usage options:")
        print("  python run.py --all         Launch both API & Dashboard")
        print("  python run.py --api         Launch FastAPI Backend (port 8000)")
        print("  python run.py --dashboard   Launch Streamlit Dashboard (port 8501)")
        print("  python run.py --pipeline    Execute reproducible end-to-end pipeline")
        print("  python run.py --journey     Verify single claim journey (CLM00001)")
        print("  python run.py --test        Run test suite")
        print("=" * 70)


if __name__ == "__main__":
    main()
