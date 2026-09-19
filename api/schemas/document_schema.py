"""
api/schemas/document_schema.py
------------------------------
Pydantic schemas for document upload, metadata persistence, and verification status.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_id: str
    claim_id: str
    document_type: str
    file_name: str
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    storage_path: str
    uploaded_by: Optional[str] = "system"
    verification_status: str = "Pending"
    created_at: Optional[str] = None
