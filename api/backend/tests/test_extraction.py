import pytest
from backend.app.services.extractor import extractor
from backend.app.schemas.environmental import EnvironmentalState

def test_extract_organic_carbon():
    text = "My soil carbon is 0.4%."
    state = extractor.extract_from_text(text)
    assert state.soil.organic_carbon_percent == 0.4

def test_extract_multiple_variables():
    text = "I have 2 hectares of wheat farmland in a semi-arid region. Rainfall is around 450 mm and soil carbon is around 0.3% with pH 7.8."
    state = extractor.extract_from_text(text)
    assert state.soil.organic_carbon_percent == 0.3
    assert state.soil.ph == 7.8
    assert state.climate.annual_rainfall_mm == 450.0
    assert state.land.crop == "wheat"
    assert state.land.land_use == "cropland"
    assert state.location.region == "semi-arid"
