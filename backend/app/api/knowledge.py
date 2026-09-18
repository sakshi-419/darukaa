from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.core.database import get_db
from backend.app.models.database_models import SourceModel
from backend.app.rag.vector_store import vector_store
from scripts.ingest_documents import ingest_all

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 4
    topic_filter: Optional[str] = None

@router.post("/search")
def search_knowledge(req: SearchRequest):
    hits = vector_store.search(req.query, top_k=req.top_k, topic_filter=req.topic_filter)
    return {"query": req.query, "results": hits, "count": len(hits)}

@router.post("/ingest")
def trigger_ingestion():
    docs = ingest_all()
    return {"status": "success", "indexed_chunks": len(docs)}

@router.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(SourceModel).all()
    res = []
    for s in sources:
        res.append({
            "id": s.id,
            "title": s.title,
            "authors": s.authors,
            "organization": s.organization,
            "year": s.year,
            "url": s.url,
            "topic": s.topic,
            "region": s.region,
            "metrics": s.metrics.split(",") if s.metrics else []
        })
    return {"sources": res, "total": len(res)}
