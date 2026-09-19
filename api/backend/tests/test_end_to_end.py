import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_scenario_1_structured_json():
    payload = {
        "soil_ph": 7.8,
        "organic_carbon": 0.3,
        "moisture": 15.0,
        "rainfall": 450.0,
        "crop": "wheat",
        "land_use": "monoculture",
        "region": "semi-arid"
    }
    response = client.post("/api/environment/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "diagnosed"
    assert len(data["recommendations"]) >= 2
    assert data["transparency"] is not None
    assert len(data["transparency"]["variables_considered"]) >= 3
    # Check recommendation structure
    rec = data["recommendations"][0]
    assert "action" in rec
    assert "why_it_works" in rec
    assert len(rec["impacted_metrics"]) >= 1
    assert len(rec["evidence"]) >= 1
    assert rec["confidence"] in ["high", "medium", "low"]

def test_scenario_2_multiturn_conversation():
    import uuid
    conv_id = f"test_dialogue_{uuid.uuid4().hex[:8]}"

    # Turn 1: "Biodiversity is declining on my farm."
    res1 = client.post("/api/chat", json={"conversation_id": conv_id, "message": "Biodiversity is declining on my farm."})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "needs_information"
    assert len(data1["clarification_questions"]) >= 3

    # Turn 2: "Carbon is 0.3%, rainfall is low and I grow wheat."
    res2 = client.post("/api/chat", json={"conversation_id": conv_id, "message": "Carbon is 0.3%, rainfall is low and I grow wheat."})
    assert res2.status_code == 200
    data2 = res2.json()
    # Should have extracted crop=wheat and carbon=0.3%
    assert data2["environmental_state"]["soil"]["organic_carbon_percent"] == 0.3
    assert data2["environmental_state"]["land"]["crop"] == "wheat"

    # Turn 3: "Around 450 mm."
    res3 = client.post("/api/chat", json={"conversation_id": conv_id, "message": "Around 450 mm."})
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["status"] == "diagnosed"
    # All 3 turns remembered!
    assert data3["environmental_state"]["soil"]["organic_carbon_percent"] == 0.3
    assert data3["environmental_state"]["land"]["crop"] == "wheat"
    assert data3["environmental_state"]["climate"]["annual_rainfall_mm"] == 450.0
    assert len(data3["recommendations"]) >= 1

def test_scenario_3_insufficient_evidence():
    res = client.post("/api/chat", json={"conversation_id": "test_scenario_3", "message": "How much will biodiversity increase if I plant 100 trees?"})
    assert res.status_code == 200
    data = res.json()
    assert "cannot be scientifically estimated" in data["overall_diagnosis"]
    assert data["insufficient_evidence_notice"] is not None
