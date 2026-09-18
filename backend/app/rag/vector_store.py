import os
import json
from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.rag.embeddings import embedding_service

class DocumentChunk:
    def __init__(self, id: str, content: str, metadata: Dict[str, Any], embedding: Optional[List[float]] = None):
        self.id = id
        self.content = content
        self.metadata = metadata
        self.embedding = embedding or []

class VectorStore:
    """
    Dual-backend Vector Database:
    Supports Qdrant with automatic ChromaDB / in-memory local fallback.
    """
    def __init__(self):
        self.db_type = settings.VECTOR_DB_TYPE
        self.qdrant_client = None
        self.chroma_collection = None
        self.in_memory_docs: List[DocumentChunk] = []
        self._init_backend()

    def _init_backend(self):
        # Attempt Qdrant if configured
        if self.db_type == "qdrant":
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.http.models import Distance, VectorParams
                
                self.qdrant_client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=3.0
                )
                collections = [c.name for c in self.qdrant_client.get_collections().collections]
                if "darukaa_knowledge" not in collections:
                    self.qdrant_client.create_collection(
                        collection_name="darukaa_knowledge",
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                    )
                print("Connected to Qdrant vector database.")
                return
            except Exception as e:
                print(f"Qdrant connection failed ({e}). Falling back to ChromaDB/in-memory.")
                self.db_type = "chroma"

        # Attempt ChromaDB
        try:
            import chromadb
            if os.getenv("VERCEL"):
                persist_dir = "/tmp/chroma_data"
            else:
                persist_dir = os.path.join(os.getcwd(), "chroma_data")
            client = chromadb.PersistentClient(path=persist_dir)
            self.chroma_collection = client.get_or_create_collection(
                name="darukaa_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            print("Connected to ChromaDB persistent vector database.")
        except Exception as e:
            print(f"ChromaDB initialization failed ({e}). Using in-memory cosine store.")
            self.db_type = "memory"

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Takes a list of documents:
        {
          "id": "...",
          "title": "...",
          "authors": "...",
          "organization": "...",
          "year": 2024,
          "content": "...",
          "url": "...",
          "topic": "...",
          "region": "...",
          "metrics": [...]
        }
        """
        for doc in documents:
            doc_id = doc.get("id") or str(len(self.in_memory_docs))
            content = doc.get("content", "")
            meta = {
                "title": doc.get("title", ""),
                "authors": doc.get("authors", ""),
                "organization": doc.get("organization", ""),
                "year": int(doc.get("year", 2023)),
                "url": doc.get("url", ""),
                "topic": doc.get("topic", "general"),
                "region": doc.get("region", "Global"),
                "metrics": ",".join(doc.get("metrics", [])) if isinstance(doc.get("metrics"), list) else str(doc.get("metrics", ""))
            }

            emb = embedding_service.get_embedding(content)
            chunk = DocumentChunk(id=doc_id, content=content, metadata=meta, embedding=emb)
            self.in_memory_docs.append(chunk)

            # Store in ChromaDB if active
            if self.chroma_collection is not None:
                try:
                    self.chroma_collection.upsert(
                        ids=[doc_id],
                        documents=[content],
                        metadatas=[meta],
                        embeddings=[emb]
                    )
                except Exception as e:
                    print(f"ChromaDB upsert notice: {e}")

            # Store in Qdrant if active
            if self.qdrant_client is not None:
                try:
                    from qdrant_client.http.models import PointStruct
                    self.qdrant_client.upsert(
                        collection_name="darukaa_knowledge",
                        points=[
                            PointStruct(
                                id=hash(doc_id) % 100000000,
                                vector=emb,
                                payload={"id": doc_id, "content": content, **meta}
                            )
                        ]
                    )
                except Exception as e:
                    print(f"Qdrant upsert notice: {e}")

    def search(self, query: str, top_k: int = 4, topic_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        query_emb = embedding_service.get_embedding(query)
        
        # Try ChromaDB query
        if self.chroma_collection is not None and self.chroma_collection.count() > 0:
            try:
                where_clause = {"topic": topic_filter} if topic_filter else None
                results = self.chroma_collection.query(
                    query_embeddings=[query_emb],
                    n_results=min(top_k, self.chroma_collection.count()),
                    where=where_clause
                )
                
                hits = []
                if results and results.get("documents") and len(results["documents"]) > 0:
                    for i, doc_text in enumerate(results["documents"][0]):
                        meta = results["metadatas"][0][i]
                        score = 1.0 - (results["distances"][0][i] if results.get("distances") else 0.2)
                        hits.append({
                            "id": results["ids"][0][i],
                            "content": doc_text,
                            "metadata": meta,
                            "score": round(float(score), 4)
                        })
                    return hits
            except Exception as e:
                print(f"Chroma query notice ({e}), falling back to in-memory cosine ranking.")

        # Fallback: In-memory cosine calculation
        import math
        def cosine_similarity(v1: List[float], v2: List[float]) -> float:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(b * b for b in v2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)

        scored = []
        for chunk in self.in_memory_docs:
            if topic_filter and chunk.metadata.get("topic") != topic_filter:
                continue
            sim = cosine_similarity(query_emb, chunk.embedding)
            scored.append({
                "id": chunk.id,
                "content": chunk.content,
                "metadata": chunk.metadata,
                "score": round(float(sim), 4)
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

vector_store = VectorStore()
