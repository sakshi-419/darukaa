from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from backend.app.core.config import settings

def _get_engine():
    db_url = settings.DATABASE_URL
    try:
        eng = create_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
        )
        with eng.connect() as conn:
            pass
        return eng
    except Exception as e:
        print(f"Database connection error on {db_url}: {e}. Trying /tmp fallback...")
        try:
            tmp_url = "sqlite:////tmp/darukaa.db"
            eng = create_engine(tmp_url, connect_args={"check_same_thread": False})
            with eng.connect() as conn:
                pass
            return eng
        except Exception as e2:
            print(f"Fallback /tmp failed ({e2}). Using in-memory SQLite.")
            return create_engine(
                "sqlite://",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )

engine = _get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

_initialized = False

def init_db():
    global _initialized, engine, SessionLocal
    try:
        Base.metadata.create_all(bind=engine)
        _initialized = True
    except Exception as e:
        print(f"init_db notice: {e}. Switching to in-memory SQLite store.")
        try:
            engine = create_engine(
                "sqlite://",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            Base.metadata.create_all(bind=engine)
            _initialized = True
        except Exception as in_mem_err:
            print(f"In-memory init error: {in_mem_err}")

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
