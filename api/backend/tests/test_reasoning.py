import pytest
from backend.app.schemas.environmental import (
    EnvironmentalState, SoilProfile, ClimateProfile, LandProfile
)
from backend.app.reasoning.multi_metric import reasoning_engine

def test_reasoning_connects_at_least_three_variables():
    state = EnvironmentalState(
        soil=SoilProfile(ph=7.8, organic_carbon_percent=0.3, moisture_percent=15.0),
        climate=ClimateProfile(annual_rainfall_mm=450.0, temperature_c=32.0),
        land=LandProfile(crop="wheat", cropping_system="monoculture")
    )
    result = reasoning_engine.reason(state)
    
    assert result["connected_variable_count"] >= 3
    assert len(result["variables_considered"]) >= 3
    assert len(result["identified_chains"]) >= 1
    # Verify presence of dryland monoculture carbon-moisture chain
    chain_names = [c.name for c in result["identified_chains"]]
    assert any("Carbon-Moisture" in name or "Agroecosystem" in name for name in chain_names)
    assert len(result["causal_pathways"]) >= 1
