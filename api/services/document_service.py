"""
api/services/document_service.py
--------------------------------
Service for document upload, secure file storage, and verification tracking.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import UploadFile

from api.db import db

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent
DOCUMENTS_STORAGE_DIR = ROOT / "data" / "documents"
DOCUMENTS_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class DocumentService:
    """Manages document uploads and metadata persistence."""

    @staticmethod
    async def save_document(
        claim_id: str,
        document_type: str,
        file: UploadFile,
        uploaded_by: str = "system",
    ) -> Dict[str, Any]:
        """Saves uploaded file to storage and creates database record."""
        claim_id = claim_id.strip()
        doc_id = str(uuid.uuid4())
        safe_filename = f"{claim_id}_{doc_id[:8]}_{file.filename}"
        dest_path = DOCUMENTS_STORAGE_DIR / safe_filename

        content = await file.read()
        with open(dest_path, "wb") as f:
            f.write(content)

        file_size = len(content)
        mime_type = file.content_type or "application/octet-stream"
        storage_rel_path = f"data/documents/{safe_filename}"

        # Ensure documents table exists if SQLite
        sql_create = """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                claim_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size_bytes INTEGER,
                mime_type TEXT,
                storage_path TEXT NOT NULL,
                uploaded_by TEXT DEFAULT 'system',
                verification_status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        db.execute(sql_create)

        insert_sql = """
            INSERT INTO documents (document_id, claim_id, document_type, file_name, file_size_bytes, mime_type, storage_path, uploaded_by, verification_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
        """
        db.execute(insert_sql, (
            doc_id,
            claim_id,
            document_type,
            file.filename,
            file_size,
            mime_type,
            storage_rel_path,
            uploaded_by,
        ))

        return {
            "document_id": doc_id,
            "claim_id": claim_id,
            "document_type": document_type,
            "file_name": file.filename,
            "file_size_bytes": file_size,
            "mime_type": mime_type,
            "storage_path": storage_rel_path,
            "uploaded_by": uploaded_by,
            "verification_status": "Pending",
        }

    @staticmethod
    def get_documents_by_claim(claim_id: str) -> List[Dict[str, Any]]:
        """Retrieves all documents associated with a claim."""
        sql_create = """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                claim_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_size_bytes INTEGER,
                mime_type TEXT,
                storage_path TEXT NOT NULL,
                uploaded_by TEXT DEFAULT 'system',
                verification_status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        db.execute(sql_create)
        return db.query_all("SELECT * FROM documents WHERE claim_id = ? ORDER BY created_at DESC", (claim_id.strip(),))
