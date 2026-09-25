"""
api/routes/auth.py
------------------
Authentication endpoints: login, register, profile inspection, and session verification.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from api.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from api.services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    """Authenticates user credentials and returns a JWT bearer access token."""
    user = AuthService.authenticate_user(req.email, req.password)
    token = AuthService.create_access_token(data={"sub": user["email"], "role": user["role_id"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role_id": user["role_id"],
            "department": user.get("department"),
            "badge_number": user.get("badge_number"),
            "is_active": True,
        },
    }


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest):
    """Registers a new user and issues an initial access token."""
    user = AuthService.register_user(
        email=req.email,
        password=req.password,
        full_name=req.full_name,
        role_id=req.role_id,
        department=req.department or "Claims & Fraud Operations",
        badge_number=req.badge_number,
    )
    token = AuthService.create_access_token(data={"sub": user["email"], "role": user["role_id"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role_id": user["role_id"],
            "department": user.get("department"),
            "badge_number": user.get("badge_number"),
            "is_active": True,
        },
    }


@router.get("/me", response_model=UserProfileResponse)
def get_current_profile(current_user: UserProfileResponse = Depends(get_current_user)):
    """Returns the authenticated user's profile and active permissions."""
    return current_user
