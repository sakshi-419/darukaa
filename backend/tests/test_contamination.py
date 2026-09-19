import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_1_baseline_wheat_monoculture():
    """
    TEST 1:
    SOC 0.3%, rainfall 450 mm, wheat, monoculture, pH 7.8, moisture 15%
    """
    payload = {
        "organic_carbon": 0.3,
        "rainfall": 450.0,
        "crop": "wheat",
        "cropping_system": "monoculture",
        "soil_ph": 7.8,
        "moisture": 15.0,
        "region": "semi-arid"
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    state = data["environmental_state"]
    assert state["soil"]["organic_carbon_percent"] == 0.3
    assert state["climate"]["annual_rainfall_mm"] == 450.0
    assert state["land"]["crop"] == "wheat"
    assert state["land"]["cropping_system"] == "monoculture"
    assert state["soil"]["ph"] == 7.8
    assert state["soil"]["moisture_percent"] == 15.0

    # Verify recommendations exist and are validated
    recs = data["recommendations"]
    assert len(recs) >= 1
    # Check that diversification of monoculture is suggested for wheat
    titles_actions = " ".join([f"{r['title']} {r['action']} {r['why_it_works']}" for r in recs])
    assert "monoculture" in titles_actions.lower()
    # Ensure unsupported quantitative claims are not present
    assert ">60% decline" not in titles_actions
    assert "15–25%" not in titles_actions
    assert "40–70%" not in titles_actions
    assert "doubling effective moisture infiltration" not in titles_actions


def test_2_chickpea_crop_rotation_zero_contamination():
    """
    TEST 2:
    SOC 0.6%, rainfall 600 mm, chickpea, crop rotation, pH 7.5, moisture 18%
    Must contain ZERO references to wheat, continuous monoculture, or previous metrics.
    Must recognize crop rotation is ALREADY being practiced.
    """
    payload = {
        "organic_carbon": 0.6,
        "rainfall": 600.0,
        "crop": "chickpea",
        "cropping_system": "crop rotation",
        "soil_ph": 7.5,
        "moisture": 18.0,
        "region": "semi-arid"
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    state = data["environmental_state"]
    
    # Assert exact inputs
    assert state["soil"]["organic_carbon_percent"] == 0.6
    assert state["climate"]["annual_rainfall_mm"] == 600.0
    assert state["land"]["crop"] == "chickpea"
    assert state["land"]["cropping_system"] == "crop rotation"
    assert state["soil"]["ph"] == 7.5
    assert state["soil"]["moisture_percent"] == 18.0

    recs = data["recommendations"]
    assert len(recs) >= 1

    all_rec_text = " ".join([f"{r['title']} {r['action']} {r['why_it_works']}" for r in recs]).lower()
    diagnosis_text = data["overall_diagnosis"].lower()
    full_output = f"{all_rec_text} {diagnosis_text}"

    # ZERO references to previous scenario crop (wheat) or continuous monoculture
    assert "wheat" not in full_output, "Contamination error: 'wheat' found in chickpea assessment!"
    assert "continuous chickpea monoculture" not in full_output
    assert "transition continuous" not in full_output, "Contamination error: told to transition from monoculture when rotation is practiced!"
    assert "introduce drought-tolerant legume" not in full_output, "Redundancy error: told to introduce legumes when crop is already chickpea!"

    # Must recognize existing crop rotation
    assert "rotation" in full_output

    # Prevent unsupported scientific claims
    assert ">60% decline" not in full_output
    assert "15–25%" not in full_output
    assert "15-25%" not in full_output
    assert "40–70%" not in full_output
    assert "40-70%" not in full_output
    assert "30–80 kg n" not in full_output
    assert "30-80 kg n" not in full_output
    assert "doubling effective moisture infiltration" not in full_output


def test_3_crop_change_only_to_wheat():
    """
    TEST 3:
    Change only the crop from chickpea to wheat:
    SOC 0.6%, rainfall 600 mm, wheat, crop rotation, pH 7.5, moisture 18%
    Recommendations must change to wheat rotation management without assuming monoculture!
    """
    payload = {
        "organic_carbon": 0.6,
        "rainfall": 600.0,
        "crop": "wheat",
        "cropping_system": "crop rotation",
        "soil_ph": 7.5,
        "moisture": 18.0,
        "region": "semi-arid"
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    recs = data["recommendations"]
    all_rec_text = " ".join([f"{r['title']} {r['action']} {r['why_it_works']}" for r in recs]).lower()

    # Must refer to wheat
    assert "wheat" in all_rec_text
    # But because system is crop rotation, must NOT say "transition continuous wheat monoculture"
    assert "transition continuous" not in all_rec_text
    assert "continuous wheat monoculture" not in all_rec_text
    # Should optimize wheat rotation
    assert "rotation" in all_rec_text


def test_4_management_change_only_to_monoculture():
    """
    TEST 4:
    Change only management from crop rotation to monoculture:
    SOC 0.6%, rainfall 600 mm, chickpea, monoculture, pH 7.5, moisture 18%
    Recommendations must appropriately address chickpea monoculture diversification.
    """
    payload = {
        "organic_carbon": 0.6,
        "rainfall": 600.0,
        "crop": "chickpea",
        "cropping_system": "monoculture",
        "soil_ph": 7.5,
        "moisture": 18.0,
        "region": "semi-arid"
    }
    res = client.post("/api/environment/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    recs = data["recommendations"]
    all_rec_text = " ".join([f"{r['title']} {r['action']} {r['why_it_works']}" for r in recs]).lower()

    # Must address chickpea monoculture
    assert "chickpea" in all_rec_text
    assert "monoculture" in all_rec_text
    # Must NOT mention wheat
    assert "wheat" not in all_rec_text


def test_5_consecutive_assessments_zero_cross_contamination():
    """
    TEST 5:
    Submit two completely different assessments consecutively through /api/chat
    and verify that assessment #2 contains ZERO values or recommendations inherited from #1.
    """
    import uuid
    conv_id = f"test_seq_{uuid.uuid4().hex[:8]}"

    # Assessment 1: Semi-arid wheat monoculture
    msg1 = "Soil organic carbon is 0.3%, annual rainfall 450 mm, growing wheat under continuous monoculture with soil pH 7.8 and moisture 15%."
    res1 = client.post("/api/chat", json={"conversation_id": conv_id, "message": msg1})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["environmental_state"]["land"]["crop"] == "wheat"
    assert data1["environmental_state"]["land"]["cropping_system"] == "monoculture"

    # Assessment 2: Completely different scenario: Chickpea with crop rotation in higher rainfall
    msg2 = "New assessment: SOC 0.6%, rainfall 600 mm, chickpea, crop rotation, pH 7.5, moisture 18%."
    res2 = client.post("/api/chat", json={"conversation_id": conv_id, "message": msg2})
    assert res2.status_code == 200
    data2 = res2.json()
    state2 = data2["environmental_state"]

    # Verify assessment 2 has ONLY new values
    assert state2["land"]["crop"] == "chickpea"
    assert state2["land"]["cropping_system"] == "crop rotation"
    assert state2["soil"]["organic_carbon_percent"] == 0.6
    assert state2["climate"]["annual_rainfall_mm"] == 600.0
    assert state2["soil"]["ph"] == 7.5
    assert state2["soil"]["moisture_percent"] == 18.0

    # Verify recommendations in assessment 2 have ZERO references to wheat or continuous monoculture
    recs2 = data2["recommendations"]
    rec2_text = " ".join([f"{r['title']} {r['action']} {r['why_it_works']}" for r in recs2]).lower()
    diag2_text = data2["overall_diagnosis"].lower()

    assert "wheat" not in rec2_text
    assert "wheat" not in diag2_text
    assert "transition continuous" not in rec2_text
    assert "continuous chickpea monoculture" not in rec2_text
