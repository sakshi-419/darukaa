import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.ingest_documents import ingest_all

def main():
    print("Initializing Darukaa.Earth Vector Index Builder...")
    docs = ingest_all()
    print(f"Successfully constructed vector index over {len(docs)} scientific chunks.")

if __name__ == "__main__":
    main()
