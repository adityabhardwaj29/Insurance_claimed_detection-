"""
run.py
------
One-Command Operational Entry Point & Startup CLI for Graph-Enhanced Insurance Fraud Detection.

Usage:
    python run.py --platform     # Launch React Frontend (3000), FastAPI (8000), and Streamlit (8501)
    python run.py --all          # Launch React Frontend (3000) and FastAPI Backend (8000)
    python run.py --frontend     # Launch Vite React Frontend on port 3000
    python run.py --api          # Launch FastAPI backend service on port 8000
    python run.py --dashboard    # Launch Streamlit interactive dashboard on port 8501
    python run.py --pipeline     # Execute reproducible end-to-end data/feature/model/case pipeline
    python run.py --journey CID  # Trace and verify complete claim journey for a specific claim ID
    python run.py --test         # Execute full pytest automated test suite
"""

from __future__ import annotations

import argparse
import os
import shutil
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


def run_frontend(port: int = 3000) -> None:
    """Launches the modern React Vite Frontend."""
    frontend_dir = ROOT / "frontend"
    npm_cmd = shutil.which("npm") or "npm"
    cmd = [npm_cmd, "run", "dev", "--", "--port", str(port)]
    print(f"\n[FRONTEND] Launching React Enterprise App on http://localhost:{port}")
    try:
        subprocess.run(cmd, cwd=str(frontend_dir), shell=True, check=True)
    except KeyboardInterrupt:
        print("\nFrontend terminated.")


def run_tests() -> None:
    """Runs the full repository automated test suite."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    print("\n[TESTS] Running full automated test suite...")
    subprocess.run(cmd)


def run_services(start_frontend: bool = True, start_api: bool = True, start_dashboard: bool = False,
                 api_port: int = 8000, frontend_port: int = 3000, dash_port: int = 8501) -> None:
    """
    Launches requested services concurrently and manages their lifecycle.
    """
    procs: list[subprocess.Popen] = []
    print("=" * 70)
    print("STARTING FRAUDSHIELD AI ENTERPRISE PLATFORM")
    print("=" * 70)

    try:
        if start_api:
            api_cmd = [
                sys.executable, "-m", "uvicorn", "api.main:app",
                "--host", "0.0.0.0", "--port", str(api_port)
            ]
            api_p = subprocess.Popen(api_cmd, cwd=str(ROOT))
            procs.append(api_p)
            print(f"[API] FastAPI server running -> http://localhost:{api_port}/docs")
            time.sleep(1.5)

        if start_dashboard:
            dash_app = ROOT / "dashboard" / "app.py"
            dash_cmd = [
                sys.executable, "-m", "streamlit", "run", str(dash_app),
                "--server.port", str(dash_port)
            ]
            dash_p = subprocess.Popen(dash_cmd, cwd=str(ROOT))
            procs.append(dash_p)
            print(f"[DASHBOARD] Streamlit console running -> http://localhost:{dash_port}")

        if start_frontend:
            npm_cmd = shutil.which("npm") or "npm"
            front_cmd = f"{npm_cmd} run dev -- --port {frontend_port}"
            front_p = subprocess.Popen(front_cmd, cwd=str(ROOT / "frontend"), shell=True)
            procs.append(front_p)
            print(f"[FRONTEND] React Enterprise UI running -> http://localhost:{frontend_port}")

        print("\nAll requested services active. Press Ctrl+C to terminate all.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down platform services...")
    finally:
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass
        print("All platform services stopped cleanly.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FraudShield AI - Enterprise Insurance Fraud Platform Master CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--platform", action="store_true", help="Launch React Frontend, FastAPI, and Streamlit")
    group.add_argument("--all", action="store_true", help="Launch React Frontend and FastAPI Backend")
    group.add_argument("--frontend", action="store_true", help="Launch React Frontend on port 3000")
    group.add_argument("--api", action="store_true", help="Launch FastAPI backend on port 8000")
    group.add_argument("--dashboard", action="store_true", help="Launch Streamlit dashboard on port 8501")
    group.add_argument("--pipeline", action="store_true", help="Run full reproducible pipeline from scratch")
    group.add_argument("--journey", type=str, nargs="?", const="CLM00001", help="Verify single claim journey (default: CLM00001)")
    group.add_argument("--test", action="store_true", help="Run automated test suite")

    parser.add_argument("--api-port", type=int, default=8000, help="Port for FastAPI server (default: 8000)")
    parser.add_argument("--frontend-port", type=int, default=3000, help="Port for React frontend (default: 3000)")
    parser.add_argument("--dash-port", type=int, default=8501, help="Port for Streamlit dashboard (default: 8501)")

    args = parser.parse_args()

    if args.platform:
        run_services(start_frontend=True, start_api=True, start_dashboard=True,
                     api_port=args.api_port, frontend_port=args.frontend_port, dash_port=args.dash_port)
    elif args.all:
        run_services(start_frontend=True, start_api=True, start_dashboard=False,
                     api_port=args.api_port, frontend_port=args.frontend_port)
    elif args.frontend:
        run_frontend(port=args.frontend_port)
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
        print("=" * 70)
        print("FRAUDSHIELD AI - ENTERPRISE INSURANCE FRAUD DETECTION PLATFORM")
        print("=" * 70)
        print("Usage options:")
        print("  python run.py --platform    Launch React (3000), FastAPI (8000), Streamlit (8501)")
        print("  python run.py --all         Launch React Frontend & FastAPI Backend")
        print("  python run.py --frontend    Launch React Frontend (port 3000)")
        print("  python run.py --api         Launch FastAPI Backend (port 8000)")
        print("  python run.py --dashboard   Launch Streamlit Dashboard (port 8501)")
        print("  python run.py --pipeline    Execute reproducible end-to-end pipeline")
        print("  python run.py --journey     Verify single claim journey (CLM00001)")
        print("  python run.py --test        Run pytest test suite")
        print("=" * 70)


if __name__ == "__main__":
    main()
