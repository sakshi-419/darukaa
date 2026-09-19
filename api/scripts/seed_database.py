import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import SessionLocal, init_db
from backend.app.models.database_models import SourceModel, Conversation, EnvironmentalProfileModel

def seed_data():
    init_db()
    db = SessionLocal()
    
    # Load scientific corpus
    corpus_file = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "documents", "scientific_corpus.json")
    if os.path.exists(corpus_file):
        with open(corpus_file, "r", encoding="utf-8") as f:
            docs = json.load(f)
            for d in docs:
                existing = db.query(SourceModel).filter_by(id=d["id"]).first()
                if not existing:
                    src = SourceModel(
                        id=d["id"],
                        title=d["title"],
                        authors=d.get("authors"),
                        organization=d["organization"],
                        year=d["year"],
                        url=d["url"],
                        source_type=d.get("source_type", "report"),
                        topic=d.get("topic", "biodiversity"),
                        region=d.get("region", "Global"),
                        content=d.get("content"),
                        metrics=",".join(d.get("metrics", []))
                    )
                    db.add(src)
        db.commit()
        print(f"Seeded scientific sources to relational database.")

    # Preload Demo Scenario 1 Profile
    demo_conv_id = "demo_semi_arid_wheat"
    existing_conv = db.query(Conversation).filter_by(id=demo_conv_id).first()
    if not existing_conv:
        conv = Conversation(
            id=demo_conv_id,
            user_id="demo_user",
            title="Semi-Arid Wheat Farmland Analysis"
        )
        profile = EnvironmentalProfileModel(
            conversation_id=demo_conv_id,
            soil_ph=7.8,
            organic_carbon=0.3,
            soil_moisture=15.0,
            rainfall=450.0,
            temperature=32.0,
            crop="wheat",
            land_use="cropland",
            cropping_system="monoculture",
            region="semi-arid",
            country="India"
        )
        db.add(conv)
        db.add(profile)
        db.commit()
        print(f"Seeded demo scenario conversation '{demo_conv_id}'.")

    db.close()

if __name__ == "__main__":
    seed_data()
