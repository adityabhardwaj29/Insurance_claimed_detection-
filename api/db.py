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
        raw_db_url = os.getenv("DATABASE_URL", "").strip()
        if not raw_db_url:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
                    raw_db_url = str(st.secrets["DATABASE_URL"]).strip()
            except Exception:
                pass
        if not raw_db_url:
            raw_db_url = "postgresql://postgres.sswdrdxforbqyvbovedw:Insurance%4012345.@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
        self.database_url = self._sanitize_db_url(raw_db_url)
        self.sqlite_path = Path(os.getenv("DATABASE_PATH", str(SQLITE_PATH)))
        self._is_postgres = bool(self.database_url and ("postgres" in self.database_url or "supabase" in self.database_url))

    @staticmethod
    def _sanitize_db_url(url: str) -> str:
        """Ensures special characters in the password are safely URL-encoded for psycopg2."""
        if not url or "@" not in url or "://" not in url:
            return url
        try:
            from urllib.parse import quote, unquote
            auth_part, _, host_part = url.rpartition("@")
            scheme, rest = auth_part.split("://", 1)
            if ":" in rest:
                user, password = rest.split(":", 1)
                enc_pwd = quote(unquote(password), safe="")
                return f"{scheme}://{user}:{enc_pwd}@{host_part}"
        except Exception:
            pass
        return url

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
                conn = psycopg2.connect(self.database_url, connect_timeout=5, cursor_factory=psycopg2.extras.RealDictCursor)
                return conn
            except Exception as e:
                # If direct Supabase fails (e.g. Render IPv4 vs Supabase direct IPv6), auto-fallback to Pooler on port 6543
                if "db." in self.database_url and ".supabase.co" in self.database_url:
                    try:
                        ref = self.database_url.split("db.", 1)[1].split(".supabase.co", 1)[0]
                        for region in ["ap-south-1", "us-east-1", "eu-central-1", "us-west-1"]:
                            pooler_url = self.database_url.replace(f"db.{ref}.supabase.co:5432", f"aws-0-{region}.pooler.supabase.com:6543")
                            pooler_url = pooler_url.replace("://postgres:", f"://postgres.{ref}:")
                            try:
                                conn = psycopg2.connect(pooler_url, connect_timeout=5, cursor_factory=psycopg2.extras.RealDictCursor)
                                self.database_url = pooler_url  # Cache working pooler URL
                                logger.info("Successfully connected to Supabase via IPv4 Pooler (%s)", region)
                                return conn
                            except Exception:
                                continue
                    except Exception as pooler_err:
                        logger.debug("Pooler auto-fallback attempt error: %s", pooler_err)
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

    def convert_sql(self, sql: str) -> str:
        """Translates SQLite query constructs to PostgreSQL when running in production."""
        converted = sql
        if self._is_postgres:
            converted = converted.replace("?", "%s")
            if "INSERT OR IGNORE INTO" in converted:
                converted = converted.replace("INSERT OR IGNORE INTO", "INSERT INTO") + " ON CONFLICT DO NOTHING"
        else:
            converted = converted.replace("%s", "?")
        return converted

    def query_all(self, sql: str, params: Optional[Union[List[Any], Tuple[Any, ...]]] = None) -> List[Dict[str, Any]]:
        """Executes a SELECT query and returns rows as dictionaries."""
        params = params or ()
        converted_sql = self.convert_sql(sql)

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
        converted_sql = self.convert_sql(sql)

        with self.connection_scope() as conn:
            cur = conn.cursor()
            cur.execute(converted_sql, params)
            return cur.rowcount


# Singleton global database instance
db = DatabaseManager()
