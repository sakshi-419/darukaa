import pytest
from backend.app.memory.clarification import clarification_engine
from backend.app.schemas.environmental import EnvironmentalState

def test_missing_information_detection():
    # User only states "My biodiversity is declining."
    state = EnvironmentalState()
    is_ready, questions = clarification_engine.evaluate(state, "My biodiversity is declining.")
    assert is_ready is False
    assert len(questions) >= 3
    assert len(questions) <= 5
    # Should ask for fundamental required variables: SOC, rainfall, crop/land use
    fields = [q.field for q in questions]
    assert "soil_organic_carbon" in fields
    assert "rainfall" in fields
