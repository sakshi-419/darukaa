from typing import Dict, Any, Optional
from backend.app.schemas.environmental import EnvironmentalState

class GeoSpatialEnrichmentService:
    """
    Geo-coordinates enrichment service (Bonus Feature):
    Maps coordinates to biome, climate zone, and estimated baseline environmental parameters.
    Allows easy plug-in for NASA Earth, Copernicus, or Open-Meteo APIs.
    """
    def enrich_from_coordinates(self, lat: float, lon: float, state: EnvironmentalState) -> EnvironmentalState:
        state.location.latitude = lat
        state.location.longitude = lon

        # Heuristic / regional lookup for demo (e.g. Rajasthan, India demo coordinates: 26.9124, 75.7873)
        if 20.0 <= lat <= 30.0 and 68.0 <= lon <= 78.0:
            state.location.country = state.location.country or "India"
            state.location.region = state.location.region or "Rajasthan (Thar / Semi-Arid Belt)"
            if state.climate.annual_rainfall_mm is None:
                state.climate.annual_rainfall_mm = 450.0
            if state.climate.temperature_c is None:
                state.climate.temperature_c = 32.0
            if state.climate.drought_risk is None:
                state.climate.drought_risk = "high"
            if state.soil.ph is None:
                state.soil.ph = 7.8
            if state.soil.organic_carbon_percent is None:
                state.soil.organic_carbon_percent = 0.35
        else:
            state.location.region = state.location.region or f"Coordinates ({lat:.2f}, {lon:.2f})"
            if state.climate.drought_risk is None:
                state.climate.drought_risk = "medium"

        return state

geo_service = GeoSpatialEnrichmentService()
