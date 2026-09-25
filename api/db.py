"""
api/db.py
---------
Unified database connection layer supporting both Supabase PostgreSQL (production)
and SQLite (local development / testing / migration source).
"""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
SQLITE_PATH = ROOT / "database" / "fraud_detection.db"


class DatabaseManager:
    """
    Manages connections to either Supabase PostgreSQL or local SQLite.
    Automatically detects environment configuration.
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "").strip()
        self.database_url = os.getenv("DATABASE_URL", "").strip()
        self.sqlite_path = Path(os.getenv("DATABASE_PATH", str(SQLITE_PATH)))
        self._is_postgres = bool(self.database_url and ("postgres" in self.database_url or "supabase" in self.database_url))

    @property
    def is_postgres(self) -> bool:
        return self._is_postgres

    @property
    def engine_type(self) -> str:
        return "Supabase PostgreSQL" if self._is_postgres else "SQLite (Local/Fallback)"

    def get_connection(self):
        """Returns a connection object appropriate for the configured engine."""
        if self._is_postgres:
            try:
                import psycopg2
                import psycopg2.extras
                conn = psycopg2.connect(self.database_url, cursor_factory=psycopg2.extras.RealDictCursor)
                return conn
            except Exception as e:
                logger.warning("Failed to connect to PostgreSQL (%s), falling back to SQLite: %s", self.database_url, e)

        # SQLite connection
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS risk_scores (
                claim_id TEXT PRIMARY KEY,
                fraud_probability REAL,
                anomaly_score REAL,
                duplicate_score REAL,
                graph_risk_score REAL,
                final_risk_score REAL,
                risk_band TEXT,
                risk_reasons TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role_id TEXT NOT NULL,
                department TEXT,
                badge_number TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS case_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id VARCHAR(30),
                event_type TEXT,
                actor TEXT,
                old_value TEXT,
                new_value TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        return conn

    @contextmanager
    def connection_scope(self) -> Generator[Any, None, None]:
        """Context manager providing a safe transaction connection scope."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def query_all(self, sql: str, params: Optional[Union[List[Any], Tuple[Any, ...]]] = None) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        params = params or ()
        # Convert parameter placeholders if using PostgreSQL (%s) vs SQLite (?)
        converted_sql = sql
        if self._is_postgres:
            converted_sql = sql.replace("?", "%s")
        else:
            converted_sql = sql.replace("%s", "?")

        with self.connection_scope() as conn:
            cur = conn.cursor()
            cur.execute(converted_sql, params)
            rows = cur.fetchall()
            if not rows:
                return []
            return [dict(r) for r in rows]

    def query_one(self, sql: str, params: Optional[Union[List[Any], Tuple[Any, ...]]] = None) -> Optional[Dict[str, Any]]:
        """Executes a SELECT query and returns a single row dictionary."""
        rows = self.query_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: Optional[Union[List[Any], Tuple[Any, ...]]] = None) -> int:
        """Executes an INSERT, UPDATE, or DELETE query and returns affected rows."""
        params = params or ()
        converted_sql = sql
        if self._is_postgres:
            converted_sql = sql.replace("?", "%s")
        else:
            converted_sql = sql.replace("%s", "?")

        with self.connection_scope() as conn:
            cur = conn.cursor()
            cur.execute(converted_sql, params)
            return cur.rowcount


# Singleton global database instance
db = DatabaseManager()
