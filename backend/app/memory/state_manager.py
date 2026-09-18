import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.database_models import Conversation, Message, EnvironmentalProfileModel
from backend.app.schemas.environmental import (
    EnvironmentalState, SoilProfile, ClimateProfile, LandProfile,
    BiodiversityProfile, HumanImpactProfile, LocationProfile
)

class StateManager:
    """
    Manages structured environmental state memory across multi-turn dialogues.
    Ensures incremental variable accumulation without data loss or duplicate questioning.
    """
    def get_or_create_conversation(self, db: Session, conversation_id: Optional[str] = None) -> Conversation:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())[:8]
        
        conv = db.query(Conversation).filter_by(id=conversation_id).first()
        if not conv:
            conv = Conversation(id=conversation_id)
            profile = EnvironmentalProfileModel(conversation_id=conversation_id)
            db.add(conv)
            db.add(profile)
            db.commit()
            db.refresh(conv)
        return conv

    def load_state(self, db: Session, conversation_id: str) -> EnvironmentalState:
        profile_row = db.query(EnvironmentalProfileModel).filter_by(conversation_id=conversation_id).first()
        if not profile_row:
            return EnvironmentalState()

        return EnvironmentalState(
            location=LocationProfile(
                country=profile_row.country,
                region=profile_row.region,
                latitude=profile_row.latitude,
                longitude=profile_row.longitude
            ),
            soil=SoilProfile(
                ph=profile_row.soil_ph,
                organic_carbon_percent=profile_row.organic_carbon,
                moisture_percent=profile_row.soil_moisture
            ),
            climate=ClimateProfile(
                annual_rainfall_mm=profile_row.rainfall,
                temperature_c=profile_row.temperature
            ),
            land=LandProfile(
                land_use=profile_row.land_use,
                crop=profile_row.crop,
                cropping_system=profile_row.cropping_system
            ),
            biodiversity=BiodiversityProfile(
                species_richness=profile_row.species_richness,
                habitat_diversity=profile_row.habitat_diversity
            ),
            human_impact=HumanImpactProfile(
                pesticide_pressure=profile_row.pesticide_pressure,
                pollution=profile_row.pollution,
                deforestation=profile_row.deforestation
            )
        )

    def merge_and_save_state(self, db: Session, conversation_id: str, new_state: EnvironmentalState) -> EnvironmentalState:
        profile_row = db.query(EnvironmentalProfileModel).filter_by(conversation_id=conversation_id).first()
        if not profile_row:
            profile_row = EnvironmentalProfileModel(conversation_id=conversation_id)
            db.add(profile_row)

        # Merge soil
        if new_state.soil.ph is not None:
            profile_row.soil_ph = new_state.soil.ph
        if new_state.soil.organic_carbon_percent is not None:
            profile_row.organic_carbon = new_state.soil.organic_carbon_percent
        if new_state.soil.moisture_percent is not None:
            profile_row.soil_moisture = new_state.soil.moisture_percent

        # Merge climate
        if new_state.climate.annual_rainfall_mm is not None:
            profile_row.rainfall = new_state.climate.annual_rainfall_mm
        if new_state.climate.temperature_c is not None:
            profile_row.temperature = new_state.climate.temperature_c

        # Merge land
        if new_state.land.land_use is not None:
            profile_row.land_use = new_state.land.land_use
        if new_state.land.crop is not None:
            profile_row.crop = new_state.land.crop
        if new_state.land.cropping_system is not None:
            profile_row.cropping_system = new_state.land.cropping_system

        # Merge biodiversity
        if new_state.biodiversity.species_richness is not None:
            profile_row.species_richness = new_state.biodiversity.species_richness
        if new_state.biodiversity.habitat_diversity is not None:
            profile_row.habitat_diversity = new_state.biodiversity.habitat_diversity

        # Merge human impact
        if new_state.human_impact.pesticide_pressure is not None:
            profile_row.pesticide_pressure = new_state.human_impact.pesticide_pressure
        if new_state.human_impact.pollution is not None:
            profile_row.pollution = new_state.human_impact.pollution

        # Merge location
        if new_state.location.country is not None:
            profile_row.country = new_state.location.country
        if new_state.location.region is not None:
            profile_row.region = new_state.location.region
        if new_state.location.latitude is not None:
            profile_row.latitude = new_state.location.latitude
        if new_state.location.longitude is not None:
            profile_row.longitude = new_state.location.longitude

        db.commit()
        db.refresh(profile_row)

        return self.load_state(db, conversation_id)

    def append_message(self, db: Session, conversation_id: str, role: str, content: str):
        msg = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(msg)
        db.commit()

state_manager = StateManager()
