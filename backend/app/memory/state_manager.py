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
    Includes in-memory fallback to guarantee zero crash in serverless/read-only environments.
    """
    def __init__(self):
        self._memory_convs: Dict[str, Conversation] = {}
        self._memory_profiles: Dict[str, EnvironmentalState] = {}
        self._memory_messages: Dict[str, list] = {}

    def get_or_create_conversation(self, db: Session, conversation_id: Optional[str] = None) -> Conversation:
        if not conversation_id:
            conversation_id = str(uuid.uuid4())[:8]
        
        try:
            conv = db.query(Conversation).filter_by(id=conversation_id).first()
            if not conv:
                conv = Conversation(id=conversation_id)
                profile = EnvironmentalProfileModel(conversation_id=conversation_id)
                db.add(conv)
                db.add(profile)
                db.commit()
                db.refresh(conv)
            return conv
        except Exception as e:
            print(f"[StateManager] Database notice in get_or_create_conversation: {e}. Using in-memory conversation.")
            try:
                db.rollback()
            except Exception:
                pass
            if conversation_id not in self._memory_convs:
                self._memory_convs[conversation_id] = Conversation(id=conversation_id)
            return self._memory_convs[conversation_id]

    def load_state(self, db: Session, conversation_id: str) -> EnvironmentalState:
        try:
            profile_row = db.query(EnvironmentalProfileModel).filter_by(conversation_id=conversation_id).first()
            if not profile_row:
                return self._memory_profiles.get(conversation_id, EnvironmentalState())

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
        except Exception as e:
            print(f"[StateManager] Database notice in load_state: {e}. Using in-memory state.")
            try:
                db.rollback()
            except Exception:
                pass
            return self._memory_profiles.get(conversation_id, EnvironmentalState())

    def merge_and_save_state(self, db: Session, conversation_id: str, new_state: EnvironmentalState) -> EnvironmentalState:
        # 1. Update in-memory cache as safeguard
        mem_state = self._memory_profiles.get(conversation_id, EnvironmentalState())
        self._apply_merge(mem_state, new_state)
        self._memory_profiles[conversation_id] = mem_state

        # 2. Persist to relational DB
        try:
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
        except Exception as e:
            print(f"[StateManager] Database notice in merge_and_save_state: {e}. Preserved in-memory state.")
            try:
                db.rollback()
            except Exception:
                pass
            return mem_state

    def append_message(self, db: Session, conversation_id: str, role: str, content: str):
        if conversation_id not in self._memory_messages:
            self._memory_messages[conversation_id] = []
        self._memory_messages[conversation_id].append({"role": role, "content": content})

        try:
            msg = Message(conversation_id=conversation_id, role=role, content=content)
            db.add(msg)
            db.commit()
        except Exception as e:
            print(f"[StateManager] Message persistence notice: {e}")
            try:
                db.rollback()
            except Exception:
                pass

    def _apply_merge(self, target: EnvironmentalState, src: EnvironmentalState):
        if src.soil.ph is not None: target.soil.ph = src.soil.ph
        if src.soil.organic_carbon_percent is not None: target.soil.organic_carbon_percent = src.soil.organic_carbon_percent
        if src.soil.moisture_percent is not None: target.soil.moisture_percent = src.soil.moisture_percent
        if src.climate.annual_rainfall_mm is not None: target.climate.annual_rainfall_mm = src.climate.annual_rainfall_mm
        if src.climate.temperature_c is not None: target.climate.temperature_c = src.climate.temperature_c
        if src.land.land_use is not None: target.land.land_use = src.land.land_use
        if src.land.crop is not None: target.land.crop = src.land.crop
        if src.land.cropping_system is not None: target.land.cropping_system = src.land.cropping_system
        if src.biodiversity.species_richness is not None: target.biodiversity.species_richness = src.biodiversity.species_richness
        if src.biodiversity.habitat_diversity is not None: target.biodiversity.habitat_diversity = src.biodiversity.habitat_diversity
        if src.human_impact.pesticide_pressure is not None: target.human_impact.pesticide_pressure = src.human_impact.pesticide_pressure
        if src.human_impact.pollution is not None: target.human_impact.pollution = src.human_impact.pollution
        if src.human_impact.deforestation is not None: target.human_impact.deforestation = src.human_impact.deforestation
        if src.location.country is not None: target.location.country = src.location.country
        if src.location.region is not None: target.location.region = src.location.region
        if src.location.latitude is not None: target.location.latitude = src.location.latitude
        if src.location.longitude is not None: target.location.longitude = src.location.longitude

state_manager = StateManager()
