import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import init_db
from backend.app.main import app

try:
    init_db()
except Exception as e:
    print(f"Vercel init_db notice: {e}")

