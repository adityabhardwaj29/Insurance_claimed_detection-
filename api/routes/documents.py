"""
api/routes/documents.py
-----------------------
Endpoints for document evidence upload, metadata retrieval, and attachment verification.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status

from api.schemas.auth_schema import UserProfileResponse
from api.services.auth_service import get_current_user
from api.services.document_service import DocumentService

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    claim_id: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = Form(...),
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """
    Uploads supporting document evidence (e.g. Claim Form, Invoice, Police Report, Damage Photo)
    and attaches metadata to the designated claim ID.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    res = await DocumentService.save_document(
        claim_id=claim_id,
        document_type=document_type,
        file=file,
        uploaded_by=current_user.full_name or current_user.email,
    )
    return res


@router.get("/claim/{claim_id}", response_model=List[Dict[str, Any]])
def get_claim_documents(
    claim_id: str,
    current_user: UserProfileResponse = Depends(get_current_user),
):
    """Retrieves all documents attached to a specific claim."""
    return DocumentService.get_documents_by_claim(claim_id)
