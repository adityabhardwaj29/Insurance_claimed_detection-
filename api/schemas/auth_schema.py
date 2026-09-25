"""
api/schemas/auth_schema.py
--------------------------
Pydantic schemas for authentication, JWT session tokens, and user profile management.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=4)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    role_id: str = Field("CLAIMS_OFFICER", pattern="^(ADMIN|CLAIMS_OFFICER|INVESTIGATOR|SUPERVISOR|ANALYST)$")
    department: Optional[str] = "Claims & Fraud Operations"
    badge_number: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role_id: str
    department: Optional[str] = None
    badge_number: Optional[str] = None
    is_active: bool = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
