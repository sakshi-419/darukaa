import pytest
from backend.app.validation.evidence_validator import evidence_validator
from backend.app.schemas.environmental import BiodiversityRecommendation, ImpactedMetric, EnvironmentalState

def test_unsupported_percentage_claim_rejection():
    query = "How much will biodiversity increase if I plant 100 trees?"
    is_rejected, refusal_notice = evidence_validator.check_unsupported_quantitative_claims(query)
    assert is_rejected is True
    assert "A reliable quantitative percentage increase cannot be scientifically estimated" in refusal_notice
    assert "Holl & Brancalion" in refusal_notice

def test_evidence_validation_with_genuine_docs():
    rec = BiodiversityRecommendation(
        id="rec_test",
        title="Legume intercrop",
        action="Introduce drought tolerant legumes",
        why_it_works="Fixes nitrogen and raises SOC",
        impacted_metrics=[
            ImpactedMetric(metric="soil_organic_carbon", direction="increase"),
            ImpactedMetric(metric="soil_moisture_retention", direction="increase")
        ],
        time_horizon={"short_term": "weeks", "medium_term": "1 yr", "long_term": "3 yr"},
        evidence=[]
    )
    docs = [
        {
            "id": "doc1",
            "title": "FAO Soil Biodiversity",
            "organization": "FAO",
            "year": 2020,
            "url": "https://fao.org",
            "content": "Legume rotations raise soil organic carbon and increase soil moisture retention.",
            "metrics": ["soil_organic_carbon", "soil_moisture"]
        }
    ]
    state = EnvironmentalState()
    is_valid, conf, notes = evidence_validator.validate_recommendation(rec, docs, state)
    assert is_valid is True
    assert conf in ["medium", "high"]
