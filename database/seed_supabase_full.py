"""
database/seed_supabase_full.py
------------------------------
Seeds the live Supabase PostgreSQL database from local SQLite database.
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQLITE_PATH = ROOT / "database" / "fraud_detection.db"
SUPABASE_URL = "postgresql://postgres:Insurance%4012345.@db.sswdrdxforbqyvbovedw.supabase.co:5432/postgres"

def main():
    print(f"Connecting to SQLite: {SQLITE_PATH}")
    s_conn = sqlite3.connect(SQLITE_PATH)
    s_conn.row_factory = sqlite3.Row
    s_cur = s_conn.cursor()

    print("Connecting to Supabase PostgreSQL...")
    p_conn = psycopg2.connect(SUPABASE_URL)
    p_cur = p_conn.cursor()

    # Disable foreign key checks for clean bulk transfer
    p_cur.execute("SET session_replication_role = 'replica';")

    # 1. Create users table in Supabase
    print("Ensuring tables in Supabase...")
    p_cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role_id TEXT NOT NULL,
            department TEXT,
            badge_number TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
    """)

    # 2. Create risk_scores table in Supabase
    p_cur.execute("""
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

    # Ensure claimants table has phone, email, address, occupation
    for col, col_type in [("phone", "TEXT"), ("email", "TEXT"), ("address", "TEXT"), ("occupation", "TEXT")]:
        try:
            p_cur.execute(f"ALTER TABLE claimants ADD COLUMN IF NOT EXISTS {col} {col_type};")
        except Exception:
            p_conn.rollback()

    p_conn.commit()

    # Transfer order respecting foreign keys
    tables = [
        "claimants",
        "providers",
        "policies",
        "vehicles",
        "invoices",
        "claims",
        "locations",
        "investigation_cases",
        "case_notes",
        "case_events",
        "users",
        "risk_scores"
    ]

    for tbl in tables:
        try:
            s_rows = s_cur.execute(f"SELECT * FROM {tbl}").fetchall()
        except Exception as e:
            print(f"Skipping {tbl} (not in sqlite): {e}")
            continue

        if not s_rows:
            print(f"No rows in sqlite for {tbl}")
            continue

        cols = [k for k in s_rows[0].keys()]
        col_str = ", ".join(cols)

        # Check existing in postgres
        p_cur.execute(f"SELECT count(*) FROM {tbl};")
        count = p_cur.fetchone()[0]
        if count > 0:
            print(f"Postgres {tbl} already has {count} rows, skipping insert.")
            continue

        print(f"Inserting {len(s_rows)} rows into Supabase {tbl}...")
        records = []
        for r in s_rows:
            row_vals = []
            for c in cols:
                v = r[c]
                if c in ("date_order_invalid", "is_active") and v is not None:
                    row_vals.append(bool(v))
                else:
                    row_vals.append(v)
            records.append(tuple(row_vals))
        
        # Build insert
        placeholders = ", ".join(["%s"] * len(cols))
        insert_query = f"INSERT INTO {tbl} ({col_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;"
        
        for rec in records:
            p_cur.execute(insert_query, rec)

        p_conn.commit()
        print(f"Successfully seeded {tbl} into Supabase.")

    p_cur.execute("SET session_replication_role = 'origin';")
    p_conn.commit()
    p_conn.close()
    s_conn.close()
    print("All tables successfully synced to Supabase!")

if __name__ == "__main__":
    main()
