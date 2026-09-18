import sys
import os

# Add root directory to python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from backend.app.core.database import init_db
    from backend.app.main import app
    try:
        init_db()
    except Exception as e:
        print(f"Vercel init_db notice: {e}")
except Exception as main_err:
    from fastapi import FastAPI
    app = FastAPI(title="Darukaa.Earth Serverless Fallback")
    
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    def fallback_route(path: str):
        return {
            "error": f"Serverless entrypoint error: {main_err}",
            "path": path
        }
