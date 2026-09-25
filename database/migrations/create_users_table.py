"""
database/migrations/create_users_table.py
-----------------------------------------
Creates the users table and seeds official officer accounts.
"""

import sqlite3
from pathlib import Path
import bcrypt

ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT / "database" / "fraud_detection.db"


def hash_pwd(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
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

    officers = [
        (
            "usr-admin-001",
            "admin@insurance.com",
            hash_pwd("admin123"),
            "System Administrator",
            "ADMIN",
            "IT & Enterprise Security",
            "SEC-ADM-001",
        ),
        (
            "usr-claims-002",
            "claims.officer@insurance.com",
            hash_pwd("claims123"),
            "Priya Sharma",
            "CLAIMS_OFFICER",
            "Claims Intake & Verification",
            "OFF-CLM-104",
        ),
        (
            "usr-investigator-003",
            "investigator@insurance.com",
            hash_pwd("investigator123"),
            "Rahul Varma, CFE",
            "INVESTIGATOR",
            "Special Investigation Unit (SIU)",
            "SIU-INV-709",
        ),
        (
            "usr-supervisor-004",
            "supervisor@insurance.com",
            hash_pwd("supervisor123"),
            "Ananya Deshmukh",
            "SUPERVISOR",
            "SIU Operations Management",
            "SIU-SUP-302",
        ),
        (
            "usr-analyst-005",
            "analyst@insurance.com",
            hash_pwd("analyst123"),
            "Vikram Malhotra",
            "ANALYST",
            "Data Science & Fraud Analytics",
            "ANL-RSK-512",
        ),
    ]

    for uid, email, phash, name, role, dept, badge in officers:
        cur.execute("""
            INSERT INTO users (id, email, password_hash, full_name, role_id, department, badge_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(email) DO UPDATE SET
                password_hash = excluded.password_hash,
                full_name = excluded.full_name,
                role_id = excluded.role_id,
                department = excluded.department,
                badge_number = excluded.badge_number;
        """, (uid, email, phash, name, role, dept, badge))

    conn.commit()
    count = cur.execute("SELECT count(*) FROM users").fetchone()[0]
    print(f"Users table created successfully. Total officers in database: {count}")
    conn.close()


if __name__ == "__main__":
    main()
