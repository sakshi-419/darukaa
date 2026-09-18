from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api import chat, environment, knowledge, health
from scripts.ingest_documents import ingest_all
from scripts.seed_database import seed_data

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Environmental Scientist delivering evidence-backed biodiversity recommendations through structured multi-metric reasoning and RAG.",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development and demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["Chat"])
app.include_router(environment.router, prefix=f"{settings.API_V1_STR}/environment", tags=["Environment"])
app.include_router(knowledge.router, prefix=f"{settings.API_V1_STR}/knowledge", tags=["Knowledge"])
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health & Telemetry"])

# Also mount sources directly under /api/sources as requested in section 19
app.add_api_route("/api/sources", knowledge.list_sources, methods=["GET"], tags=["Knowledge"])

@app.on_event("startup")
def on_startup():
    print("Starting Darukaa.Earth Backend...")
    init_db()
    seed_data()
    # Ingest documents if vector store empty
    try:
        ingest_all()
    except Exception as e:
        print(f"Ingestion warning on startup: {e}")
    print("Darukaa.Earth Backend is fully ready.")

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main.py:app", host="0.0.0.0", port=8000, reload=True)
