import uuid
import logging
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from api.models import DocumentUploadResponse
from agents.rag_agent import RAGAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/document", tags=["documents"])


class DocumentQueryRequest(BaseModel):
    query: str


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        content = await file.read()
        suffix = os.path.splitext(file.filename or "")[1] or ".txt"

        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=suffix) as f:
            f.write(content)
            temp_path = f.name

        try:
            rag = RAGAgent()
            result = rag.ingest_document(temp_path, collection_name="document_store")

            doc_id = result.get("doc_id", str(uuid.uuid4()))
            chunks_stored = result.get("chunks_count", 0)

            return DocumentUploadResponse(
                doc_id=doc_id,
                chunks_stored=chunks_stored,
                status="stored"
            )
        finally:
            os.unlink(temp_path)

    except Exception:
        logger.exception("Document upload failed")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.post("/query")
async def query_document(req: DocumentQueryRequest):
    try:
        rag = RAGAgent()
        return rag.answer_question(req.query)
    except Exception:
        logger.exception("Document query failed")
        raise HTTPException(status_code=500, detail="Query failed")
