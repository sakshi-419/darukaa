import re
from typing import Dict, Any, Optional
from backend.app.schemas.environmental import (
    EnvironmentalState, SoilProfile, ClimateProfile, LandProfile,
    LocationProfile, HumanImpactProfile, BiodiversityProfile
)

class EnvironmentalExtractor:
    """
    Extracts structured environmental variables strictly from the current text.
    Ensures zero carry-over or contamination across independent assessments.
    """
    def extract_from_text(
        self,
        text: str,
        existing_state: Optional[EnvironmentalState] = None,
        force_fresh: bool = False
    ) -> EnvironmentalState:
        # Check if the text contains a self-contained assessment
        is_substantive_assessment = self.is_substantive_assessment(text)
        
        # If forced fresh or if the text is a substantive assessment, do NOT inherit old state
        if force_fresh or is_substantive_assessment or existing_state is None:
            state = EnvironmentalState()
        else:
            # Deep clone existing state to prevent in-place mutation
            state = existing_state.model_copy(deep=True)

        text_lower = text.lower()

        # 1. Soil pH extraction (e.g. "ph 7.8", "soil ph: 7.5", "ph is 7.5", "ph=7.5", "ph 7.5")
        ph_match = re.search(r'(?:soil\s*)?ph\s*(?:is|=|:|\s+of)?\s*([0-9]+(?:\.[0-9]+)?)', text_lower)
        if ph_match:
            try:
                val = float(ph_match.group(1))
                if 3.0 <= val <= 11.0:
                    state.soil.ph = val
            except ValueError:
                pass

        # 2. Soil Organic Carbon (SOC) (e.g. "soc 0.6%", "carbon is 0.3%", "organic carbon: 0.6%", "0.6% soc", "soc: 0.6%")
        soc_match = re.search(r'(?:soil\s*)?(?:organic\s*carbon|soc|carbon)(?:[^0-9%]*?(?:is|was|=|:|\s+of|\s+around|\s+about|\s+at|\s+approx))?\s*([0-9]+(?:\.[0-9]+)?)\s*%', text_lower)
        if not soc_match:
            soc_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:soil\s*)?(?:organic\s*carbon|carbon|soc)', text_lower)
        if not soc_match:
            soc_match = re.search(r'\bsoc\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\s*%', text_lower)
        if soc_match:
            try:
                state.soil.organic_carbon_percent = float(soc_match.group(1))
            except ValueError:
                pass

        # 3. Soil Moisture (e.g. "moisture 18%", "soil moisture 15%", "18% moisture", "moisture: 18%")
        moisture_match = re.search(r'(?:soil\s*)?moisture\s*(?:is|=|:|\s+of)?\s*([0-9]+(?:\.[0-9]+)?)\s*%', text_lower)
        if not moisture_match:
            moisture_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:soil\s*)?moisture', text_lower)
        if moisture_match:
            try:
                state.soil.moisture_percent = float(moisture_match.group(1))
            except ValueError:
                pass

        # 4. Rainfall (e.g. "rainfall 600 mm", "600 mm", "600 mm/year", "rainfall: 450 mm")
        rainfall_match = re.search(r'(?:annual\s*)?(?:rainfall|precipitation)\s*(?:is|=|:|\s+around|\s+about)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:mm|millimeters)?', text_lower)
        if not rainfall_match:
            rainfall_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:mm|millimeters)(?:\s*(?:/|per)\s*(?:year|yr|annum))?', text_lower)
        if not rainfall_match and ("around" in text_lower or "about" in text_lower):
            near_mm = re.search(r'(?:around|about)\s*([0-9]+(?:\.[0-9]+)?)\s*mm', text_lower)
            if near_mm:
                rainfall_match = near_mm
        if rainfall_match:
            try:
                val = float(rainfall_match.group(1))
                if val >= 10:  # Avoid matching small percentages or single digits
                    state.climate.annual_rainfall_mm = val
            except ValueError:
                pass

        # 5. Temperature
        temp_match = re.search(r'(?:temperature|temp)\s*(?:is|=|:)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:°?c|degrees)?', text_lower)
        if temp_match:
            try:
                state.climate.temperature_c = float(temp_match.group(1))
            except ValueError:
                pass

        # 6. Crops / Vegetation
        crop_catalog = [
            ("chickpea", ["chickpea", "cicer arietinum", "chana", "garbanzo", "gram"]),
            ("pigeonpea", ["pigeonpea", "cajanus cajan", "arhar", "tur", "red gram"]),
            ("lentil", ["lentil", "masoor", "lens culinaris"]),
            ("cowpea", ["cowpea", "lobiya"]),
            ("pea", ["pea", "peas", "matar"]),
            ("soybean", ["soybean", "soya"]),
            ("groundnut", ["groundnut", "peanut"]),
            ("wheat", ["wheat", "triticum"]),
            ("rice", ["rice", "paddy", "oryza"]),
            ("maize", ["maize", "corn", "zea mays"]),
            ("barley", ["barley"]),
            ("millet", ["millet", "bajra", "pearl millet", "finger millet", "ragi", "foxtail millet"]),
            ("sorghum", ["sorghum", "jowar"]),
            ("cotton", ["cotton", "gossypium"]),
            ("mustard", ["mustard", "sarson", "rapeseed", "canola", "brassica"]),
            ("tea", ["tea", "camellia sinensis"]),
            ("coffee", ["coffee"]),
            ("sugarcane", ["sugarcane", "cane"]),
            ("sunflower", ["sunflower"]),
            ("pulses", ["pulses", "legumes", "legume"])
        ]
        
        detected_crop = None
        for canonical_name, syns in crop_catalog:
            for s in syns:
                if re.search(r'\b' + re.escape(s) + r'\b', text_lower):
                    detected_crop = canonical_name
                    break
            if detected_crop:
                break

        if detected_crop:
            state.land.crop = detected_crop
            if not state.land.land_use:
                state.land.land_use = "cropland"

        # 7. Cropping System / Management System
        if re.search(r'\b(?:crop\s+rotation|rotational\s+cropping|crop\s+rotations|crop-rotation|rotation)\b', text_lower):
            state.land.cropping_system = "crop rotation"
        elif re.search(r'\b(?:monoculture|continuous\s+monoculture|single\s+crop|sole\s+cropping)\b', text_lower):
            state.land.cropping_system = "monoculture"
        elif re.search(r'\b(?:intercropping|intercrop|strip-intercropping|strip\s+intercropping|mixed\s+cropping)\b', text_lower):
            state.land.cropping_system = "intercropping"
        elif re.search(r'\b(?:agroforestry|silvopasture|alley\s+cropping)\b', text_lower):
            state.land.cropping_system = "agroforestry"
            state.land.land_use = "agroforestry"

        # Land use check
        if re.search(r'\b(?:cropland|farmland|field|farm)\b', text_lower):
            state.land.land_use = "cropland"
        elif re.search(r'\b(?:forest|woodland)\b', text_lower):
            state.land.land_use = "forest"
        elif re.search(r'\b(?:grassland|pasture)\b', text_lower):
            state.land.land_use = "grassland"

        # 8. Region / Biome / Location
        if "rajasthan" in text_lower:
            state.location.region = "Rajasthan, semi-arid"
            state.location.country = "India"
            state.climate.seasonality = "semi-arid"
        elif "semi-arid" in text_lower or "semi arid" in text_lower:
            state.location.region = "semi-arid"
            state.climate.seasonality = "semi-arid"
        elif "arid" in text_lower:
            state.location.region = "arid"
            state.climate.seasonality = "arid"
        elif "tropical" in text_lower:
            state.location.region = "tropical"
            state.climate.seasonality = "tropical"
        elif "temperate" in text_lower:
            state.location.region = "temperate"
            state.climate.seasonality = "temperate"

        # 9. Human Impact / Pesticide Pressure (only if explicitly stated)
        if re.search(r'\b(?:high\s+pesticide|heavy\s+pesticide|intensive\s+chemical)\b', text_lower):
            state.human_impact.pesticide_pressure = "high"
        elif re.search(r'\b(?:low\s+pesticide|no\s+pesticide|organic)\b', text_lower):
            state.human_impact.pesticide_pressure = "low"

        return state

    def is_substantive_assessment(self, text: str) -> bool:
        """
        Determines if the text contains a substantive environmental assessment input
        (rather than an incremental single-parameter clarification like 'Around 450 mm').
        """
        text_lower = text.lower()
        signals = 0
        if re.search(r'(?:soc|organic\s*carbon|\bcarbon\b)', text_lower) and "%" in text_lower:
            signals += 1
        if re.search(r'\b(?:rainfall|precipitation|\d+\s*mm)\b', text_lower):
            signals += 1
        if re.search(r'\b(?:ph\s*[0-9]|soil\s*ph)\b', text_lower):
            signals += 1
        if re.search(r'\b(?:moisture\s*[0-9]|\d+%\s*moisture)\b', text_lower):
            signals += 1
        if re.search(r'\b(?:chickpea|wheat|rice|cotton|maize|crop\s+rotation|monoculture|intercropping)\b', text_lower):
            signals += 1
        
        # If user provides >= 2 distinct environmental signals, it's an assessment
        return signals >= 2

extractor = EnvironmentalExtractor()
