import pytest
from backend.app.rag.retrieval import rag_retriever
from backend.app.schemas.environmental import (
    EnvironmentalState, SoilProfile, ClimateProfile, LandProfile
)

def test_rag_retrieval_and_subquery_generation():
    state = EnvironmentalState(
        soil=SoilProfile(organic_carbon_percent=0.3, moisture_percent=14.0),
        climate=ClimateProfile(annual_rainfall_mm=450.0),
        land=LandProfile(crop="wheat", cropping_system="monoculture")
    )
    subqueries = rag_retriever.generate_subqueries("farmland biodiversity", state)
    assert len(subqueries) >= 3
    # Check that multi-dimensional concepts were generated
    combined = " ".join(subqueries).lower()
    assert "carbon" in combined
    assert "moisture" in combined or "drought" in combined

    # Retrieve docs
    hits = rag_retriever.retrieve_evidence("farmland biodiversity", state, top_k=3)
    assert len(hits) > 0
    # Must contain authoritative organizations
    orgs = [h["organization"] for h in hits]
    assert any(o in ["FAO", "IPBES", "IPCC", "UNEP", "Science / AAAS", "Nature Geoscience / Peer-Reviewed"] for o in orgs)
