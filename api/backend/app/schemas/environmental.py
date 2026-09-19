from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LocationProfile(BaseModel):
    country: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SoilProfile(BaseModel):
    ph: Optional[float] = Field(None, description="Soil pH level (typically 3.5 - 10.0)")
    organic_carbon_percent: Optional[float] = Field(None, description="Soil organic carbon percentage (SOC %)")
    moisture_percent: Optional[float] = Field(None, description="Volumetric soil moisture percentage")
    microbial_activity: Optional[str] = Field(None, description="Low, Moderate, High or qualitative assessment")
    erosion_risk: Optional[str] = Field(None, description="Low, Moderate, Severe")

class ClimateProfile(BaseModel):
    annual_rainfall_mm: Optional[float] = Field(None, description="Average annual precipitation in mm")
    temperature_c: Optional[float] = Field(None, description="Mean temperature in Celsius")
    drought_risk: Optional[str] = Field(None, description="Low, Medium, High, Extreme")
    seasonality: Optional[str] = Field(None, description="Arid, Semi-arid, Tropical, Temperate")

class LandProfile(BaseModel):
    land_use: Optional[str] = Field(None, description="cropland, forest, grassland, wetland, agroforestry")
    crop: Optional[str] = Field(None, description="Primary crop (e.g. wheat, rice, maize, cotton)")
    cropping_system: Optional[str] = Field(None, description="monoculture, crop_rotation, intercropping, agroforestry")
    canopy_cover_percent: Optional[float] = Field(None, description="Percentage canopy cover")
    habitat_fragmentation: Optional[str] = Field(None, description="Low, Moderate, High")

class BiodiversityProfile(BaseModel):
    species_richness: Optional[int] = Field(None, description="Estimated number of observed species")
    habitat_diversity: Optional[str] = Field(None, description="Low, Medium, High")
    pollinator_abundance: Optional[str] = Field(None, description="Low, Moderate, Abundant")
    functional_diversity: Optional[str] = Field(None, description="Qualitative functional guild presence")

class HumanImpactProfile(BaseModel):
    pesticide_pressure: Optional[str] = Field(None, description="Low, Moderate, High, Intensive")
    fertilizer_intensity: Optional[str] = Field(None, description="Low, Moderate, High")
    deforestation: Optional[str] = Field(None, description="None, Historical, Active")
    groundwater_extraction: Optional[str] = Field(None, description="Sustainable, Overexploited, Critical")
    pollution: Optional[str] = Field(None, description="Qualitative pollution pressure")

class EnvironmentalState(BaseModel):
    location: LocationProfile = Field(default_factory=LocationProfile)
    soil: SoilProfile = Field(default_factory=SoilProfile)
    climate: ClimateProfile = Field(default_factory=ClimateProfile)
    land: LandProfile = Field(default_factory=LandProfile)
    biodiversity: BiodiversityProfile = Field(default_factory=BiodiversityProfile)
    human_impact: HumanImpactProfile = Field(default_factory=HumanImpactProfile)

# Flat input schema for POST /api/environment/analyze
class EnvironmentAnalyzeRequest(BaseModel):
    soil_ph: Optional[float] = None
    organic_carbon: Optional[float] = None
    moisture: Optional[float] = None
    rainfall: Optional[float] = None
    temperature: Optional[float] = None
    crop: Optional[str] = None
    land_use: Optional[str] = None
    cropping_system: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    pesticide_pressure: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ImpactedMetric(BaseModel):
    metric: str
    direction: str = "increase"  # increase (↑) or decrease (↓)
    expected_time: str = "medium_term"  # short_term, medium_term, long_term
    scientific_basis: Optional[str] = None

class ScientificEvidence(BaseModel):
    title: str
    organization: str
    authors: Optional[str] = "Scientific Research Panel"
    year: int
    url: str
    relevance: str
    source_type: str = "report"
    metrics_supported: List[str] = Field(default_factory=list)

class BiodiversityRecommendation(BaseModel):
    id: str
    title: str
    action: str
    why_it_works: str
    impacted_metrics: List[ImpactedMetric]
    time_horizon: Dict[str, str]  # {"short_term": "...", "medium_term": "...", "long_term": "..."}
    evidence: List[ScientificEvidence]
    confidence: str = "medium"  # low, medium, high
    confidence_rationale: Optional[str] = None
    connected_variables: List[str] = Field(default_factory=list)

class CausalRelationship(BaseModel):
    step: int
    source_variable: str
    target_variable: str
    mechanism: str
    direction: str

class TransparencyTrace(BaseModel):
    user_inputs: Dict[str, Any]
    variables_considered: List[str]
    relationships_identified: List[str]
    causal_chains: List[List[str]]
    retrieved_sources_count: int
    relevant_sources_used: int
    evidence_validation_summary: str
    confidence_breakdown: Dict[str, Any]

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    geo_coords: Optional[Dict[str, float]] = None

class ClarificationQuestion(BaseModel):
    field: str
    priority: str  # required, useful, optional
    question: str
    unit_or_format: str

class ChatResponse(BaseModel):
    conversation_id: str
    status: str  # "needs_information" or "diagnosed"
    overall_diagnosis: Optional[str] = None
    clarification_questions: List[str] = Field(default_factory=list)
    structured_questions: List[ClarificationQuestion] = Field(default_factory=list)
    environmental_state: EnvironmentalState
    recommendations: List[BiodiversityRecommendation] = Field(default_factory=list)
    causal_pathways: List[str] = Field(default_factory=list)
    transparency: Optional[TransparencyTrace] = None
    insufficient_evidence_notice: Optional[str] = None
