"""
api/services/auth_service.py
----------------------------
Authentication and Role-Based Access Control (RBAC) service.
Provides JWT issuance, password hashing, and user authentication with Supabase/local fallback.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt

from api.db import db
from api.schemas.auth_schema import UserProfileResponse

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-for-insurance-fraud-intelligence-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8"))
    except Exception:
        return False


# In-memory demo profiles registry for instant local access
DEMO_USERS: Dict[str, Dict[str, Any]] = {
    "admin@insurance.com": {
        "id": "usr-admin-001",
        "email": "admin@insurance.com",
        "full_name": "System Administrator",
        "role_id": "ADMIN",
        "department": "IT & Security",
        "password_hash": hash_password("admin123"),
    },
    "claims.officer@insurance.com": {
        "id": "usr-claims-002",
        "email": "claims.officer@insurance.com",
        "full_name": "Priya Sharma",
        "role_id": "CLAIMS_OFFICER",
        "department": "Claim Intake",
        "password_hash": hash_password("claims123"),
    },
    "investigator@insurance.com": {
        "id": "usr-investigator-003",
        "email": "investigator@insurance.com",
        "full_name": "Rahul Varma",
        "role_id": "INVESTIGATOR",
        "department": "Special Investigation Unit",
        "password_hash": hash_password("investigator123"),
    },
    "supervisor@insurance.com": {
        "id": "usr-supervisor-004",
        "email": "supervisor@insurance.com",
        "full_name": "Ananya Deshmukh",
        "role_id": "SUPERVISOR",
        "department": "SIU Management",
        "password_hash": hash_password("supervisor123"),
    },
    "analyst@insurance.com": {
        "id": "usr-analyst-005",
        "email": "analyst@insurance.com",
        "full_name": "Vikram Malhotra",
        "role_id": "ANALYST",
        "department": "Data Science & Risk Analytics",
        "password_hash": hash_password("analyst123"),
    },
}


class AuthService:
    """Manages user authentication and tokens."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return hash_password(password)


    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        norm_email = email.lower().strip()
        # 1. Check in database users table
        try:
            row = db.query_one("SELECT * FROM users WHERE lower(email) = ?", (norm_email,))
            if row:
                return {
                    "id": str(row.get("id")),
                    "email": row.get("email"),
                    "full_name": row.get("full_name"),
                    "role_id": row.get("role_id", "CLAIMS_OFFICER"),
                    "department": row.get("department"),
                    "badge_number": row.get("badge_number"),
                    "password_hash": row.get("password_hash"),
                    "is_active": bool(row.get("is_active", 1)),
                }
        except Exception as e:
            logger.debug("Users query failed: %s", e)

        # 2. Check in DEMO_USERS memory cache
        if norm_email in DEMO_USERS:
            return DEMO_USERS[norm_email]

        return None

    @staticmethod
    def register_user(
        email: str,
        password: str,
        full_name: str,
        role_id: str,
        department: str,
        badge_number: Optional[str] = None
    ) -> Dict[str, Any]:
        norm_email = email.lower().strip()
        if AuthService.get_user_by_email(norm_email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An officer account with this email already exists"
            )

        user_id = f"usr-{int(time.time())}-{os.urandom(2).hex()}"
        pwd_hash = AuthService.hash_password(password)
        if not badge_number:
            badge_number = f"OFF-{role_id[:3]}-{int(time.time()) % 10000:04d}"

        new_user = {
            "id": user_id,
            "email": norm_email,
            "full_name": full_name,
            "role_id": role_id,
            "department": department or "Special Operations",
            "badge_number": badge_number,
            "password_hash": pwd_hash,
            "is_active": True,
        }

        try:
            db.execute("""
                INSERT INTO users (id, email, password_hash, full_name, role_id, department, badge_number, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """, (user_id, norm_email, pwd_hash, full_name, role_id, department, badge_number))
        except Exception as e:
            logger.error("Failed to insert user into DB: %s", e)

        DEMO_USERS[norm_email] = new_user
        return new_user

    @staticmethod
    def authenticate_user(email: str, password: str) -> Dict[str, Any]:
        user = AuthService.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid officer credentials: email not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not AuthService.verify_password(password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid officer credentials: password does not match",
                headers={"WWW-Authenticate": "Bearer"},
            )
        try:
            db.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user["id"],))
        except Exception:
            pass
        return user


def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> UserProfileResponse:
    """Dependency for extracting and validating the authenticated user."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = AuthService.get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return UserProfileResponse(
        id=str(user["id"]),
        email=user["email"],
        full_name=user["full_name"],
        role_id=user["role_id"],
        department=user.get("department"),
        badge_number=user.get("badge_number"),
        is_active=True,
    )


def require_role(allowed_roles: List[str]):
    """Role-based authorization dependency factory."""
    def role_checker(current_user: UserProfileResponse = Depends(get_current_user)) -> UserProfileResponse:
        if current_user.role_id not in allowed_roles and current_user.role_id != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of {allowed_roles}, but user has role {current_user.role_id}"
            )
        return current_user
    return role_checker
