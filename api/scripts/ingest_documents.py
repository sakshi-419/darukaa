import os
import sys
import json
import csv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.rag.vector_store import vector_store

def parse_json(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return [data]

def parse_txt_md(filepath: str):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse simple header metadata if available
    lines = content.split("\n")
    metadata = {
        "title": filename.replace("_", " ").replace(".txt", "").replace(".md", "").title(),
        "authors": "Scientific Advisory",
        "organization": "Environmental Research Group",
        "year": 2023,
        "url": "https://www.fao.org/global-soil-partnership/en/",
        "topic": "soil_biodiversity",
        "metrics": ["soil_organic_carbon", "biodiversity"]
    }

    body = []
    for line in lines:
        if line.startswith("**Organization:**") or line.startswith("Organization:"):
            metadata["organization"] = line.split(":", 1)[1].strip().replace("**", "")
        elif line.startswith("**Year:**") or line.startswith("Year:"):
            try:
                metadata["year"] = int(line.split(":", 1)[1].strip().replace("**", ""))
            except:
                pass
        elif line.startswith("**URL:**") or line.startswith("URL:"):
            metadata["url"] = line.split(":", 1)[1].strip()
        elif line.startswith("**Topic:**") or line.startswith("Topic:"):
            metadata["topic"] = line.split(":", 1)[1].strip()
        elif line.startswith("**Metrics:**") or line.startswith("Metrics:"):
            raw_metrics = line.split(":", 1)[1].strip()
            metadata["metrics"] = [m.strip() for m in raw_metrics.split(",")]
        else:
            body.append(line)

    return [{
        "id": filename.replace(".", "_"),
        "title": metadata["title"],
        "authors": metadata["authors"],
        "organization": metadata["organization"],
        "year": metadata["year"],
        "url": metadata["url"],
        "topic": metadata["topic"],
        "metrics": metadata["metrics"],
        "content": "\n".join(body).strip()
    }]

def parse_csv(filepath: str):
    docs = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            metric = row.get("metric", "")
            implication = row.get("ecological_implication", "")
            src = row.get("source", "FAO")
            crit = row.get("threshold_critical", "")
            opt = row.get("threshold_optimal", "")
            unit = row.get("unit", "")
            
            content = f"Environmental metric: {metric}. Critical threshold: {crit} {unit}. Optimal threshold: {opt} {unit}. Ecological implication: {implication}."
            docs.append({
                "id": f"threshold_{metric}_{i}",
                "title": f"Ecological Threshold: {metric.replace('_', ' ').title()}",
                "authors": "Environmental Standards Council",
                "organization": src,
                "year": 2022,
                "url": "https://www.fao.org/soils-portal/en/",
                "topic": "ecological_thresholds",
                "metrics": [metric],
                "content": content
            })
    return docs

def ingest_all():
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "documents")
    sample_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "sample_data")
    
    all_docs = []

    # Read documents directory
    if os.path.exists(docs_dir):
        for fname in os.listdir(docs_dir):
            fpath = os.path.join(docs_dir, fname)
            if fname.endswith(".json"):
                all_docs.extend(parse_json(fpath))
            elif fname.endswith(".txt") or fname.endswith(".md"):
                all_docs.extend(parse_txt_md(fpath))

    # Read sample data directory
    if os.path.exists(sample_dir):
        for fname in os.listdir(sample_dir):
            fpath = os.path.join(sample_dir, fname)
            if fname.endswith(".csv"):
                all_docs.extend(parse_csv(fpath))

    print(f"Loaded {len(all_docs)} scientific knowledge chunks.")
    vector_store.add_documents(all_docs)
    print("Vector database indexing complete!")
    return all_docs

if __name__ == "__main__":
    ingest_all()
