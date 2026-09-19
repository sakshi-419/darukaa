import re
from typing import Dict, Any, Optional
from backend.app.schemas.environmental import EnvironmentalState

class EnvironmentalExtractor:
    """
    Extracts structured environmental variables from natural language or semi-structured text.
    Uses precise regex patterns and ecological ontology matching.
    """
    def extract_from_text(self, text: str, existing_state: Optional[EnvironmentalState] = None) -> EnvironmentalState:
        state = existing_state or EnvironmentalState()
        text_lower = text.lower()

        # 1. Soil pH extraction (e.g. "ph 7.8", "ph is 6.5", "ph of 7.2", "soil ph: 7.5")
        ph_match = re.search(r'(?:soil\s*)?ph\s*(?:is|=|:|\s+of)?\s*([0-9]+(?:\.[0-9]+)?)', text_lower)
        if ph_match:
            try:
                val = float(ph_match.group(1))
                if 3.0 <= val <= 11.0:
                    state.soil.ph = val
            except ValueError:
                pass

        # 2. Soil Organic Carbon (SOC) (e.g. "carbon is 0.3%", "soil carbon is around 0.3%", "soc 0.4%", "organic carbon: 0.5%")
        soc_match = re.search(r'(?:soil\s*)?(?:organic\s*carbon|soc|carbon)(?:[^0-9%]*?(?:is|was|=|:|\s+of|\s+around|\s+about|\s+at|\s+approx))?\s*([0-9]+(?:\.[0-9]+)?)\s*%', text_lower)
        if not soc_match:
            soc_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:soil\s*)?(?:organic\s*carbon|carbon|soc)', text_lower)
        if soc_match:
            try:
                state.soil.organic_carbon_percent = float(soc_match.group(1))
            except ValueError:
                pass

        # 3. Soil Moisture (e.g. "moisture 15%", "soil moisture is 12%")
        moisture_match = re.search(r'(?:soil\s*)?moisture\s*(?:is|=|:|\s+of)?\s*([0-9]+(?:\.[0-9]+)?)\s*%', text_lower)
        if moisture_match:
            try:
                state.soil.moisture_percent = float(moisture_match.group(1))
            except ValueError:
                pass

        # 4. Rainfall (e.g. "rainfall 450 mm", "400 mm rainfall", "around 450 mm", "rainfall is around 400mm")
        rainfall_match = re.search(r'(?:rainfall|precipitation)\s*(?:is|=|:|\s+around|\s+about)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:mm|millimeters)?', text_lower)
        if not rainfall_match:
            rainfall_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:mm|millimeters)\s*(?:annual\s*)?(?:rainfall|precipitation)?', text_lower)
        if not rainfall_match and ("around" in text_lower or "about" in text_lower):
            near_mm = re.search(r'(?:around|about)\s*([0-9]+(?:\.[0-9]+)?)\s*mm', text_lower)
            if near_mm:
                rainfall_match = near_mm
        if rainfall_match:
            try:
                val = float(rainfall_match.group(1))
                if val > 10:  # Avoid matching percentages or single digits
                    state.climate.annual_rainfall_mm = val
            except ValueError:
                pass

        # 5. Temperature (e.g. "32 c", "30 degrees", "temperature 32C")
        temp_match = re.search(r'(?:temperature|temp)\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:°?c|degrees)?', text_lower)
        if temp_match:
            try:
                state.climate.temperature_c = float(temp_match.group(1))
            except ValueError:
                pass

        # 6. Crops
        common_crops = ["wheat", "rice", "maize", "corn", "soybean", "cotton", "barley", "millet", "sorghum", "pulses", "sugarcane"]
        for crop in common_crops:
            if re.search(r'\b' + crop + r'\b', text_lower):
                state.land.crop = crop
                if not state.land.land_use:
                    state.land.land_use = "cropland"
                break

        # 7. Land use & Cropping System
        if "monoculture" in text_lower or "single crop" in text_lower:
            state.land.cropping_system = "monoculture"
        elif "intercropping" in text_lower or "intercrop" in text_lower or "mixed cropping" in text_lower:
            state.land.cropping_system = "intercropping"
        elif "agroforestry" in text_lower:
            state.land.cropping_system = "agroforestry"
            state.land.land_use = "agroforestry"

        if "cropland" in text_lower or "farmland" in text_lower or "farm" in text_lower:
            state.land.land_use = "cropland"
        elif "forest" in text_lower or "woodland" in text_lower:
            state.land.land_use = "forest"
        elif "grassland" in text_lower or "pasture" in text_lower:
            state.land.land_use = "grassland"

        # 8. Region / Biome / Climate descriptors
        if "semi-arid" in text_lower or "semi arid" in text_lower:
            state.location.region = "semi-arid"
            state.climate.seasonality = "semi-arid"
            state.climate.drought_risk = "high"
        elif "arid" in text_lower:
            state.location.region = "arid"
            state.climate.seasonality = "arid"
            state.climate.drought_risk = "extreme"
        elif "tropical" in text_lower:
            state.location.region = "tropical"
            state.climate.seasonality = "tropical"

        # 9. Human pressure / Pesticide
        if "high pesticide" in text_lower or "heavy pesticide" in text_lower or "frequent spray" in text_lower:
            state.human_impact.pesticide_pressure = "high"
        elif "no pesticide" in text_lower or "organic" in text_lower:
            state.human_impact.pesticide_pressure = "low"

        # 10. Qualitative moisture/rainfall hints if exact number not present
        if state.climate.annual_rainfall_mm is None:
            if "low rainfall" in text_lower or "dry" in text_lower or "drought" in text_lower:
                state.climate.drought_risk = "high"
                if "dry" in text_lower and state.soil.moisture_percent is None:
                    state.soil.moisture_percent = 15.0

        return state

extractor = EnvironmentalExtractor()
