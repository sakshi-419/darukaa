import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base
from backend.app.memory.state_manager import StateManager
from backend.app.services.extractor import extractor

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_multiturn_memory_accumulation(db):
    sm = StateManager()
    conv_id = "test_conv_123"
    sm.get_or_create_conversation(db, conv_id)

    # Turn 1: User says "I have wheat farmland."
    state1 = extractor.extract_from_text("I have wheat farmland.")
    sm.merge_and_save_state(db, conv_id, state1)
    stored = sm.load_state(db, conv_id)
    assert stored.land.crop == "wheat"

    # Turn 2: User says "Rainfall is around 400 mm."
    state2 = extractor.extract_from_text("Rainfall is around 400 mm.")
    sm.merge_and_save_state(db, conv_id, state2)
    stored = sm.load_state(db, conv_id)
    assert stored.land.crop == "wheat"  # Retained from turn 1!
    assert stored.climate.annual_rainfall_mm == 400.0

    # Turn 3: User says "Organic carbon is 0.3%."
    state3 = extractor.extract_from_text("Organic carbon is 0.3%.")
    sm.merge_and_save_state(db, conv_id, state3)
    stored = sm.load_state(db, conv_id)
    assert stored.land.crop == "wheat"
    assert stored.climate.annual_rainfall_mm == 400.0
    assert stored.soil.organic_carbon_percent == 0.3
