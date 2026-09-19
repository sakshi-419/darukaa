import os
import shutil
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from backend.app.core.config import settings, is_serverless

def _prepare_tmp_sqlite():
    """Copy bundled darukaa.db into /tmp if running in serverless environment."""
    tmp_path = "/tmp/darukaa.db"
    if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
        return
    src_candidates = [
        "/var/task/darukaa.db",
        "/var/task/api/darukaa.db",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../darukaa.db")),
        os.path.abspath(os.path.join(os.getcwd(), "darukaa.db")),
    ]
    for src in src_candidates:
        if os.path.isfile(src):
            try:
                shutil.copy2(src, tmp_path)
                try:
                    os.chmod(tmp_path, 0o666)
                except Exception:
                    pass
                print(f"[Database] Seeded /tmp/darukaa.db from {src}")
                break
            except Exception as e:
                print(f"[Database] Notice copying {src} to {tmp_path}: {e}")

def _test_engine_writable(eng, is_sqlite: bool):
    with eng.connect() as conn:
        conn.execute(text("SELECT 1"))
        if is_sqlite:
            conn.execute(text("CREATE TABLE IF NOT EXISTS _darukaa_health (id INTEGER PRIMARY KEY);"))
            conn.commit()

def _get_engine():
    serverless = is_serverless()
    if serverless:
        _prepare_tmp_sqlite()
        target_url = "sqlite:////tmp/darukaa.db"
    else:
        target_url = getattr(settings, "effective_database_url", settings.DATABASE_URL)

    # 1. Attempt target_url
    try:
        is_sqlite = "sqlite" in target_url and target_url != "sqlite://"
        connect_args = {"check_same_thread": False} if "sqlite" in target_url else {}
        eng = create_engine(target_url, connect_args=connect_args)
        _test_engine_writable(eng, is_sqlite)
        print(f"[Database] Successfully connected to {target_url}")
        return eng
    except Exception as e1:
        print(f"[Database] Connection error on {target_url}: {e1}")

    # 2. Attempt /tmp if not already tried
    if target_url != "sqlite:////tmp/darukaa.db":
        try:
            _prepare_tmp_sqlite()
            tmp_url = "sqlite:////tmp/darukaa.db"
            eng = create_engine(tmp_url, connect_args={"check_same_thread": False})
            _test_engine_writable(eng, True)
            print(f"[Database] Fallback connected to {tmp_url}")
            return eng
        except Exception as e2:
            print(f"[Database] Fallback /tmp failed: {e2}")

    # 3. Final fallback: in-memory SQLite with StaticPool (no disk access required)
    print("[Database] Using in-memory SQLite with StaticPool fallback.")
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
        print(f"[Database] init_db notice: {e}. Switching to in-memory StaticPool.")
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
            print(f"[Database] In-memory init error: {in_mem_err}")

def get_db():
    global _initialized
    if not _initialized:
        init_db()
        try:
            from scripts.seed_database import seed_data
            seed_data()
        except Exception as e:
            print(f"[Database] Auto-seeding notice: {e}")
        _initialized = True

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
