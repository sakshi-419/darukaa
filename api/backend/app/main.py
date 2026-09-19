from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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

# Global Exception Boundary to prevent unhandled crashes
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    err_tb = traceback.format_exc()
    print(f"Server error on {request.url.path}: {err_tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Application error: {str(exc)}",
            "error_type": type(exc).__name__,
            "path": request.url.path,
            "traceback": err_tb
        }
    )

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development and demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers (mounted with and without /api prefix for bulletproof Vercel serverless routing)
app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["Chat"])
app.include_router(chat.router, prefix="", tags=["Chat"])

app.include_router(environment.router, prefix=f"{settings.API_V1_STR}/environment", tags=["Environment"])
app.include_router(environment.router, prefix="/environment", tags=["Environment"])

app.include_router(knowledge.router, prefix=f"{settings.API_V1_STR}/knowledge", tags=["Knowledge"])
app.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge"])

app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health & Telemetry"])
app.include_router(health.router, prefix="", tags=["Health & Telemetry"])

# Also mount sources directly under /api/sources and /sources
app.add_api_route("/api/sources", knowledge.list_sources, methods=["GET"], tags=["Knowledge"])
app.add_api_route("/sources", knowledge.list_sources, methods=["GET"], tags=["Knowledge"])

@app.on_event("startup")
def on_startup():
    print("Starting Darukaa.Earth Backend...")
    try:
        init_db()
    except Exception as e:
        print(f"init_db notice on startup: {e}")
    try:
        seed_data()
    except Exception as e:
        print(f"seed_data notice on startup: {e}")
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
