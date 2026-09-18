import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

for p in [ROOT_DIR, os.getcwd()]:
    if p and p not in sys.path:
        sys.path.insert(0, p)

from backend.app.main import app
