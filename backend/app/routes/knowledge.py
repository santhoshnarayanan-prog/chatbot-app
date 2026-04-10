import logging
import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.knowledge_model import KnowledgeSource
from app.services.knowledge_service import (
    add_to_knowledge_base,
    crawl_website,
    delete_source_chunks,
    parse_docx,
    parse_pdf,
    parse_txt,
)

router = APIRouter()
logger = logging.getLogger(__name__)

_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


class WebsiteRequest(BaseModel):
    url: str
    name: str


# ── Upload document ────────────────────────────────────────────────────────────

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only PDF, DOCX, and TXT files are supported.")

    content_bytes = await file.read()

    try:
        if ext == ".pdf":
            text = parse_pdf(content_bytes)
        elif ext == ".docx":
            text = parse_docx(content_bytes)
        else:
            text = parse_txt(content_bytes)
    except Exception as e:
        raise HTTPException(422, f"Could not parse file: {e}")

    if not text.strip():
        raise HTTPException(422, "No readable text found in the uploaded file.")

    source = KnowledgeSource(
        name=file.filename,
        source_type="document",
        url_or_filename=file.filename,
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    try:
        chunks = add_to_knowledge_base(text, source.id, source.name, "document")
    except Exception as e:
        db.delete(source)
        db.commit()
        raise HTTPException(500, f"Failed to index document: {e}")

    source.chunks_count = chunks
    db.commit()

    logger.info("Document '%s' indexed — %d chunks", file.filename, chunks)
    return {"id": source.id, "name": source.name, "chunks": chunks}


# ── Add website ────────────────────────────────────────────────────────────────

@router.post("/website")
async def add_website(req: WebsiteRequest, db: Session = Depends(get_db)):
    try:
        text = crawl_website(req.url)
    except Exception as e:
        raise HTTPException(400, f"Failed to crawl website: {e}")

    if not text.strip():
        raise HTTPException(422, "No readable content found on the page.")

    source = KnowledgeSource(
        name=req.name,
        source_type="website",
        url_or_filename=req.url,
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    try:
        chunks = add_to_knowledge_base(text, source.id, source.name, "website")
    except Exception as e:
        db.delete(source)
        db.commit()
        raise HTTPException(500, f"Failed to index website: {e}")

    source.chunks_count = chunks
    db.commit()

    logger.info("Website '%s' indexed — %d chunks", req.name, chunks)
    return {"id": source.id, "name": source.name, "chunks": chunks}


# ── List sources ───────────────────────────────────────────────────────────────

@router.get("/sources")
async def list_sources(db: Session = Depends(get_db)):
    sources = (
        db.query(KnowledgeSource)
        .order_by(KnowledgeSource.created_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "type": s.source_type,
            "source": s.url_or_filename,
            "chunks": s.chunks_count,
            "added_at": s.created_at.isoformat(),
        }
        for s in sources
    ]


# ── Delete source ──────────────────────────────────────────────────────────────

@router.delete("/sources/{source_id}")
async def delete_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()
    if not source:
        raise HTTPException(404, "Knowledge source not found.")

    delete_source_chunks(source_id)
    db.delete(source)
    db.commit()

    logger.info("Deleted knowledge source id=%d (%s)", source_id, source.name)
    return {"deleted": source_id}
