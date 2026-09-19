import pytest
import re
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.validation.evidence_validator import evidence_validator
from backend.app.schemas.environmental import (
    EnvironmentalState, SoilProfile, ClimateProfile, LandProfile, BiodiversityRecommendation, ScientificEvidence
)

client = TestClient(app)

def test_1_cotton_monoculture_scientific_calibration():
    """
    Test 1 — Cotton monoculture
    SOC: 0.25%
    Rainfall: 500 mm
    Crop: Cotton
    pH: 7.9
    Management: Continuous monoculture
    Moisture: 13%

    Verify:
    - low SOC recognized
    - monoculture recognized
    - alkaline pH recognized
    - water limitation considered
    - no invented microbial measurements
    - no invented nutrient deficiencies
    - no unsupported percentages
    """
    payload = {
        "organic_carbon": 0.25,
        "rainfall": 500.0,
        "crop": "Cotton",
        "cropping_system": "Continuous monoculture",
        "soil_ph": 7.9,
        "moisture": 13.0
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    diagnosis = data["overall_diagnosis"]
    recs = data["recommendations"]
    all_text = diagnosis + " " + " ".join([f"{r['title']} {r['action']} {r['why_it_works']}" for r in recs])
    all_text_lower = all_text.lower()

    # 1. Low SOC recognized
    assert "0.25" in all_text or "soc" in all_text_lower or "organic carbon" in all_text_lower

    # 2. Monoculture recognized
    assert "monoculture" in all_text_lower

    # 3. Alkaline pH recognized
    assert "7.9" in all_text or "alkaline" in all_text_lower

    # 4. Water limitation considered
    assert any(term in all_text_lower for term in ["water", "moisture", "rainfall", "500"])

    # 5. No invented microbial measurements
    assert "microbial biomass >" not in all_text_lower
    assert "declined by 60%" not in all_text_lower
    assert "collapsed" not in all_text_lower
    assert "collapse of soil structure" not in all_text_lower

    # 6. No invented nutrient deficiencies (must treat as potential availability / soil testing needed, not proven deficiency)
    assert "soil is zinc deficient" not in all_text_lower
    assert "is zinc deficient" not in all_text_lower
    assert "is phosphorus deficient" not in all_text_lower
    assert "soil is phosphorus deficient" not in all_text_lower

    # 7. No unsupported percentages
    unsupported_pcts = ["20%", "60%", "15–25%", "15-25%", "40–70%", "40-70%"]
    for up in unsupported_pcts:
        assert up not in all_text, f"Found unsupported percentage '{up}' in output"


def test_2_agroforestry_calibration():
    """
    Test 2 — Agroforestry
    SOC: 1.2%
    Rainfall: 350 mm
    Crop: Pearl millet + native trees
    pH: 8.1
    Management: Agroforestry
    Moisture: 12%

    Verify:
    - existing agroforestry recognized
    - system does not recommend converting to agroforestry
    - SOC is not incorrectly described as severely depleted
    - water limitation recognized
    - alkaline pH treated as a potential nutrient-availability issue, not proof of deficiency
    """
    payload = {
        "organic_carbon": 1.2,
        "rainfall": 350.0,
        "crop": "Pearl millet + native trees",
        "cropping_system": "Agroforestry",
        "soil_ph": 8.1,
        "moisture": 12.0
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    diagnosis = data["overall_diagnosis"]
    recs = data["recommendations"]
    all_text = diagnosis + " " + " ".join([f"{r['title']} {r['action']} {r['why_it_works']}" for r in recs])
    all_text_lower = all_text.lower()

    # 1. Existing agroforestry recognized
    assert "agroforestry" in all_text_lower

    # 2. System does NOT recommend converting to agroforestry or transitioning monoculture
    assert "convert the farm to agroforestry" not in all_text_lower
    assert "convert to agroforestry" not in all_text_lower
    assert "transition continuous monoculture" not in all_text_lower

    # 3. SOC is NOT incorrectly described as severely depleted (1.2% is moderate/adequate)
    assert "severely depleted" not in all_text_lower
    assert "severe degradation" not in all_text_lower

    # 4. Water limitation recognized (350 mm semi-arid)
    assert any(term in all_text_lower for term in ["semi-arid", "arid", "350", "moisture", "water"])

    # 5. Alkaline pH treated as potential availability constraint, not proof of deficiency
    assert "is zinc deficient" not in all_text_lower
    assert "is phosphorus deficient" not in all_text_lower
    assert any(term in all_text_lower for term in ["availability", "soil testing", "alkaline"])


def test_3_acidic_rice_regime_and_isolation():
    """
    Test 3 — Acidic rice
    SOC: 0.7%
    Rainfall: 1000 mm
    Crop: Rice
    pH: 5.2
    Management: Crop rotation
    Moisture: 32%

    Verify:
    - acidic pH recognized
    - alkaline-soil diagnosis is NOT generated
    - high rainfall is not described as severe drought
    - no previous scenario information leaks into the response
    """
    payload = {
        "organic_carbon": 0.7,
        "rainfall": 1000.0,
        "crop": "Rice",
        "cropping_system": "Crop rotation",
        "soil_ph": 5.2,
        "moisture": 32.0
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    diagnosis = data["overall_diagnosis"]
    recs = data["recommendations"]
    all_text = diagnosis + " " + " ".join([f"{r['title']} {r['action']} {r['why_it_works']}" for r in recs])
    all_text_lower = all_text.lower()

    # 1. Acidic pH recognized
    assert "acidic" in all_text_lower or "5.2" in all_text

    # 2. Alkaline-soil diagnosis is NOT generated
    assert "alkaline" not in all_text_lower

    # 3. High rainfall (1000 mm) is NOT described as severe drought
    assert "severe drought" not in all_text_lower
    assert "arid" not in all_text_lower
    assert "contour furrow" not in all_text_lower

    # 4. No previous scenario information leaks into response (wheat, cotton, pearl millet)
    assert "cotton" not in all_text_lower
    assert "wheat" not in all_text_lower
    assert "pearl millet" not in all_text_lower


def test_4_unsupported_numerical_claims():
    """
    Test 4 — Unsupported numerical claim
    Give the system a scenario where no source supports a numerical improvement.
    Verify that it does NOT invent a percentage.
    """
    payload = {
        "organic_carbon": 0.5,
        "rainfall": 600.0,
        "crop": "Sorghum",
        "cropping_system": "Crop rotation",
        "soil_ph": 6.8,
        "moisture": 20.0
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    recs = data["recommendations"]

    for r in recs:
        # Check that action does not promise fixed percentage improvements
        assert not re.search(r'\b(?:will\s+increase|increases)\s+by\s+\d+%', r["action"].lower()), (
            f"Found unsupported percentage increase in action: {r['action']}"
        )
        assert not re.search(r'\b(?:will\s+increase|increases)\s+by\s+\d+%', r["why_it_works"].lower()), (
            f"Found unsupported percentage increase in why_it_works: {r['why_it_works']}"
        )
        # Check that impacted metrics do not contain fabricated percentage changes
        for m in r["impacted_metrics"]:
            assert "↑ Increase" != m["direction"]
            assert not re.search(r'\b\d+%', m["scientific_basis"] or "")

    # Also test query asking for direct percentage prediction
    detected, notice = evidence_validator.check_unsupported_quantitative_claims(
        "How much percentage will biodiversity increase if I plant 100 trees?"
    )
    assert detected is True
    assert "cannot be scientifically estimated" in notice


def test_5_missing_information_transparency():
    """
    Test 5 — Missing information
    Remove pH, moisture and soil texture.
    Verify that the system does NOT invent them and instead identifies them as unknown.
    """
    payload = {
        "organic_carbon": 0.4,
        "rainfall": 550.0,
        "crop": "Maize",
        "cropping_system": "Monoculture"
        # soil_ph, moisture, texture omitted
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    diagnosis = data["overall_diagnosis"]
    diagnosis_lower = diagnosis.lower()

    # Verify that unmeasured variables section is included and explicitly states unknown/not provided
    assert "unmeasured variables" in diagnosis_lower or "cannot be determined" in diagnosis_lower
    assert "not provided" in diagnosis_lower or "unmeasured" in diagnosis_lower
    assert "ph" in diagnosis_lower
    assert "soil moisture" in diagnosis_lower or "moisture" in diagnosis_lower
    assert "texture" in diagnosis_lower


def test_6_evidence_mismatch_and_strength_validation():
    """
    Test 6 — Evidence mismatch
    Provide a general soil-health source that does not support a claimed numerical improvement.
    Verify that the system does NOT use that source as evidence for the numerical claim.
    Also verify evidence classification (Class A, B, C, D) and evidence strength levels.
    """
    state = EnvironmentalState(
        soil=SoilProfile(organic_carbon_percent=0.25, ph=7.9, moisture_percent=13.0),
        climate=ClimateProfile(annual_rainfall_mm=500.0),
        land=LandProfile(crop="Cotton", cropping_system="monoculture")
    )

    general_doc = {
        "title": "General Agroecology Overview",
        "content": "Conservation agriculture generally improves soil organic carbon and soil health.",
        "organization": "FAO"
    }

    # Test claim classification:
    claims = [
        "User reports SOC of 0.25%",                         # Class A
        "Residue retention can improve soil organic matter",  # Class B
        "Low SOC may contribute to reduced moisture buffering", # Class C
        "Microbial biomass has declined by 60%",             # Class D (unsupported percentage & microbial collapse)
        "Soil is zinc deficient"                             # Class D (unsupported deficiency diagnosis)
    ]

    classified = evidence_validator.classify_claims(claims, state, [general_doc])
    assert "User reports SOC of 0.25%" in classified["Class A"]
    assert "Residue retention can improve soil organic matter" in classified["Class B"]
    assert "Low SOC may contribute to reduced moisture buffering" in classified["Class C"]
    assert "Microbial biomass has declined by 60%" in classified["Class D"]
    assert "Soil is zinc deficient" in classified["Class D"]

    # Test recommendation validation does not allow fabricated 20% claim to stand with general doc
    test_rec = BiodiversityRecommendation(
        id="rec_test",
        title="Crop Residue Retention",
        action="Retain crop residues to improve soil cover.",
        time_horizon={"short_term": "1-2 seasons", "medium_term": "3-5 seasons", "long_term": "5+ seasons"},
        why_it_works="Residue retention will increase soil moisture retention by 20%.",
        impacted_metrics=[],
        evidence=[
            ScientificEvidence(
                title=general_doc["title"],
                authors="Smith et al.",
                year=2021,
                organization="FAO",
                url="https://fao.org/conservation-ag",
                key_finding="Conservation agriculture generally improves soil organic carbon.",
                relevance="General soil health",
                metrics_supported=["soil_organic_carbon"]
            )
        ],
        confidence="high",
        evidence_strength="Strong evidence"
    )

    validated = evidence_validator.validate_and_filter_recommendations([test_rec], state, [general_doc])
    assert len(validated) == 1
    # Check that the 20% claim was sanitized
    assert "20%" not in validated[0].why_it_works
    assert "can contribute to improved levels" in validated[0].why_it_works or "improving" in validated[0].why_it_works
