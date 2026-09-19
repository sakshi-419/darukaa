from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

_initialized = False

def init_db():
    global _initialized
    try:
        Base.metadata.create_all(bind=engine)
        _initialized = True
    except Exception as e:
        print(f"init_db notice: {e}")

def get_db():
    global _initialized
    if not _initialized:
        init_db()
        try:
            from scripts.seed_database import seed_data
            from scripts.ingest_documents import ingest_all
            seed_data()
            ingest_all()
        except Exception as e:
            print(f"Auto-seeding notice: {e}")
            _initialized = True

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
