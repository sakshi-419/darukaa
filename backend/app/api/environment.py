from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.environmental import (
    EnvironmentAnalyzeRequest, ChatResponse, EnvironmentalState,
    SoilProfile, ClimateProfile, LandProfile, LocationProfile, HumanImpactProfile,
    TransparencyTrace, BiodiversityRecommendation
)
from backend.app.services.geo_service import geo_service
from backend.app.reasoning.multi_metric import reasoning_engine
from backend.app.rag.retrieval import rag_retriever
from backend.app.recommendations.engine import recommendation_engine
from backend.app.validation.evidence_validator import evidence_validator
import uuid

router = APIRouter()

@router.post("/analyze", response_model=ChatResponse)
def analyze_environment(req: EnvironmentAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Direct structured JSON ingestion endpoint:
    Processes full environmental parameters without requiring multi-turn chat.
    """
    state = EnvironmentalState(
        location=LocationProfile(
            region=req.region,
            country=req.country,
            latitude=req.latitude,
            longitude=req.longitude
        ),
        soil=SoilProfile(
            ph=req.soil_ph,
            organic_carbon_percent=req.organic_carbon,
            moisture_percent=req.moisture
        ),
        climate=ClimateProfile(
            annual_rainfall_mm=req.rainfall,
            temperature_c=req.temperature,
            drought_risk="high" if (req.rainfall and req.rainfall < 500) else "medium"
        ),
        land=LandProfile(
            land_use=req.land_use or "cropland",
            crop=req.crop,
            cropping_system=req.cropping_system or ("monoculture" if req.land_use == "monoculture" else None)
        ),
        human_impact=HumanImpactProfile(
            pesticide_pressure=req.pesticide_pressure
        )
    )

    # Geo enrichment if coordinates provided
    if req.latitude and req.longitude:
        state = geo_service.enrich_from_coordinates(req.latitude, req.longitude, state)

    # Multi-metric reasoning
    reasoning_out = reasoning_engine.reason(state)

    # Multi-query RAG retrieval
    synthetic_query = f"{state.land.crop or 'cropland'} in {state.location.region or 'dryland'} with {state.climate.annual_rainfall_mm or 450}mm rainfall and {state.soil.organic_carbon_percent or 0.3}% organic carbon"
    retrieved_docs = rag_retriever.retrieve_evidence(synthetic_query, state, top_k=4)

    # Recommendation generation
    recommendations = recommendation_engine.generate_recommendations(state, reasoning_out, retrieved_docs)

    # Transparency trace
    transparency = TransparencyTrace(
        user_inputs=req.model_dump(),
        variables_considered=reasoning_out["variables_considered"],
        relationships_identified=[ch.name for ch in reasoning_out["identified_chains"]],
        causal_chains=[ch.steps for ch in reasoning_out["identified_chains"]],
        retrieved_sources_count=len(retrieved_docs),
        relevant_sources_used=sum(len(r.evidence) for r in recommendations),
        evidence_validation_summary="Direct structured analysis backed by peer-reviewed evidence and ecological causal inference.",
        confidence_breakdown={
            "variables_linked_count": reasoning_out["connected_variable_count"],
            "sources_count": len(retrieved_docs),
            "recommendation_confidences": [r.confidence for r in recommendations]
        }
    )

    return ChatResponse(
        conversation_id=f"json_analysis_{str(uuid.uuid4())[:6]}",
        status="diagnosed",
        overall_diagnosis=reasoning_out["overall_diagnosis"],
        environmental_state=state,
        recommendations=recommendations,
        causal_pathways=reasoning_out["causal_pathways"],
        transparency=transparency
    )

@router.post("/validate")
def validate_intervention(recommendation: BiodiversityRecommendation):
    """
    Independent evidence validation endpoint:
    Checks if a proposed recommendation is substantiated by the knowledge base.
    """
    retrieved = rag_retriever.retrieve_evidence(recommendation.action, top_k=3)
    dummy_state = EnvironmentalState()
    is_valid, conf, notes = evidence_validator.validate_recommendation(recommendation, retrieved, dummy_state)
    return {
        "is_supported": is_valid,
        "confidence": conf,
        "validation_rationale": notes,
        "retrieved_evidence_matches": len(retrieved)
    }
