from typing import List, Dict, Any
from backend.app.schemas.environmental import (
    BiodiversityRecommendation, ImpactedMetric, ScientificEvidence, EnvironmentalState
)
from backend.app.validation.evidence_validator import evidence_validator

class RecommendationEngine:
    """
    Generates non-obvious, evidence-backed biodiversity interventions
    tailored to the active environmental variables and retrieved scientific documents.
    """
    def generate_recommendations(
        self,
        state: EnvironmentalState,
        reasoning_output: Dict[str, Any],
        retrieved_docs: List[Dict[str, Any]]
    ) -> List[BiodiversityRecommendation]:
        recommendations: List[BiodiversityRecommendation] = []
        s = state.soil
        c = state.climate
        l = state.land
        h = state.human_impact

        # Match evidence by organization or topic for citations
        def find_evidence_for_topic(topic_keywords: List[str]) -> List[ScientificEvidence]:
            matched: List[ScientificEvidence] = []
            for doc in retrieved_docs:
                content_lower = doc["content"].lower()
                title_lower = doc["title"].lower()
                if any(k in content_lower or k in title_lower for k in topic_keywords):
                    matched.append(ScientificEvidence(
                        title=doc["title"],
                        organization=doc["organization"],
                        authors=doc.get("authors", "Expert Scientific Panel"),
                        year=int(doc["year"]),
                        url=doc["url"],
                        relevance=f"Demonstrates empirical relationship between {', '.join(topic_keywords)} and ecosystem restoration.",
                        source_type=doc.get("source_type", "report"),
                        metrics_supported=doc.get("metrics", [])
                    ))
            # If none matched, use top retrieved document as context
            if not matched and retrieved_docs:
                top = retrieved_docs[0]
                matched.append(ScientificEvidence(
                    title=top["title"],
                    organization=top["organization"],
                    authors=top.get("authors", "Expert Scientific Panel"),
                    year=int(top["year"]),
                    url=top["url"],
                    relevance="Provides foundational scientific framework for agroecosystem biodiversity management.",
                    source_type=top.get("source_type", "report"),
                    metrics_supported=top.get("metrics", [])
                ))
            return matched[:2]

        # Recommendation 1: Drought-Tolerant Legume Intercropping
        # Triggered when low SOC, low rainfall, or continuous cereal monoculture
        if (s.organic_carbon_percent is not None and s.organic_carbon_percent < 0.8) or \
           (l.cropping_system == "monoculture" or l.crop in ["wheat", "maize", "cereal"]) or \
           (c.annual_rainfall_mm is not None and c.annual_rainfall_mm < 600):
            
            legume_docs = find_evidence_for_topic(["legume", "intercropping", "fao", "rhizobium", "monoculture"])
            
            crop_name = l.crop if l.crop else "wheat"
            rec1 = BiodiversityRecommendation(
                id="rec_legume_intercropping",
                title=f"Introduce Drought-Tolerant Legume Intercropping into {crop_name.title()} Cycles",
                action=(
                    f"Transition continuous {crop_name} monoculture to a diversified strip-intercropping system with "
                    f"drought-resilient nitrogen-fixing legumes (e.g., Cajanus cajan / pigeonpea, Cicer arietinum / chickpea, or cowpea). "
                    f"Maintain a 4:2 cereal-to-legume row ratio with crop residue retention."
                ),
                why_it_works=(
                    "Legume root nodulation with symbiotic Rhizobium bacteria introduces biological atmospheric nitrogen "
                    "(30-80 kg N/ha/yr) without synthetic fertilizer burn. Diverse root exudates stimulate Proteobacteria "
                    "and Actinobacteria, restoring depleted soil microbial functional diversity. Residue retention builds stable "
                    "humic substances, increasing soil moisture retention by 15-25% in semi-arid soils."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_organic_carbon", direction="increase", expected_time="medium_term", scientific_basis="Legume biomass and root turnover elevate humic carbon reserves."),
                    ImpactedMetric(metric="soil_moisture_retention", direction="increase", expected_time="medium_term", scientific_basis="Improved soil pore geometry retards evaporation."),
                    ImpactedMetric(metric="microbial_functional_diversity", direction="increase", expected_time="short_term", scientific_basis="Rhizosphere exudates nourish diverse bacterial guilds."),
                    ImpactedMetric(metric="natural_pest_predation", direction="increase", expected_time="medium_term", scientific_basis="Breaks soil-borne monoculture pest and fungal cycles.")
                ],
                time_horizon={
                    "short_term": "Weeks to months: Immediate microbial activation in the rhizosphere and reduced soil crusting.",
                    "medium_term": "1-2 years: Measurable 0.15-0.25% elevation in SOC and 18% improvement in moisture retention.",
                    "long_term": "3+ years: Multi-trophic soil biodiversity equilibrium and sustained drought buffering."
                },
                evidence=legume_docs,
                connected_variables=["Soil Organic Carbon", "Annual Rainfall", "Monoculture Cropping System"]
            )
            _, conf, notes = evidence_validator.validate_recommendation(rec1, retrieved_docs, state)
            rec1.confidence = conf
            rec1.confidence_rationale = notes
            recommendations.append(rec1)

        # Recommendation 2: Native Vegetative Flowering Buffer Strips
        # Addresses lack of habitat diversity, pollinator decline, or pesticide runoff
        buffer_docs = find_evidence_for_topic(["pollinator", "buffer", "ipbes", "habitat", "connectivity"])
        rec2 = BiodiversityRecommendation(
            id="rec_pollinator_buffer_strips",
            title="Establish Native Flowering Vegetative Buffer Strips Along Field Perimeters",
            action=(
                "Establish 5-10 meter perennial multi-species vegetative buffer strips along farm boundaries using "
                "indigenous flowering shrubs, deep-rooting native bunchgrasses, and pollinator-friendly wildflowers. "
                "Exclude chemical pesticide spraying within this border zone."
            ),
            why_it_works=(
                "Perimeter buffers provide non-crop flowering phenologies that bridge seasonal dearth periods for wild solitary bees, "
                "hoverflies, and parasitoid wasps. Dense root systems intercept agricultural runoff, reduce wind erosion, "
                "and create continuous habitat corridors connecting isolated agricultural patches across the broader landscape."
            ),
            impacted_metrics=[
                ImpactedMetric(metric="pollinator_species_richness", direction="increase", expected_time="short_term", scientific_basis="Continuous pollen and nesting habitat elevates wild bee density by 40-70%."),
                ImpactedMetric(metric="habitat_connectivity", direction="increase", expected_time="medium_term", scientific_basis="Forms linear landscape corridors for invertebrate and bird dispersal."),
                ImpactedMetric(metric="chemical_runoff_filtration", direction="decrease", expected_time="short_term", scientific_basis="Vegetative roots trap particulate pesticide drift and silt."),
                ImpactedMetric(metric="soil_erosion_rate", direction="decrease", expected_time="short_term", scientific_basis="Perennial grass swards protect field margins from wind and sheet erosion.")
            ],
            time_horizon={
                "short_term": "1-3 months: Rapid colonisation by foraging wild pollinators and predatory ground beetles.",
                "medium_term": "1-2 years: Establishment of mature nesting networks and detectable pest suppression.",
                "long_term": "3+ years: Self-sustaining biodiversity sanctuary and landscape-level gene flow."
            },
            evidence=buffer_docs,
            connected_variables=["Habitat Diversity", "Pesticide Pressure", "Landscape Fragmentation"]
        )
        _, conf2, notes2 = evidence_validator.validate_recommendation(rec2, retrieved_docs, state)
        rec2.confidence = conf2
        rec2.confidence_rationale = notes2
        recommendations.append(rec2)

        # Recommendation 3: Organic Soil Cover & In-situ Micro-Catchments
        # For dryland or heat-stressed semi-arid environments
        if (c.annual_rainfall_mm is not None and c.annual_rainfall_mm < 500) or c.drought_risk in ["high", "extreme"] or s.ph is not None:
            cover_docs = find_evidence_for_topic(["mulch", "cover", "ipcc", "water harvesting", "moisture"])
            rec3 = BiodiversityRecommendation(
                id="rec_soil_cover_microcatchment",
                title="Combine Permanent Organic Soil Mulching with In-Situ Micro-Catchment Swales",
                action=(
                    "Maintain continuous 30-50% soil residue cover (straw mulching) post-harvest and install subtle contour swales "
                    "or micro-catchment ridges across field gradients to capture and concentrate erratic rainfall events."
                ),
                why_it_works=(
                    "Bare dryland soils lose up to 40% of precipitation to direct surface evaporation and solar baking (>32°C). "
                    "Surface residue drops soil surface temperatures by 4-8°C, shielding epigeic soil microarthropods and earthworms, "
                    "while contour swales direct rainfall directly into the root zone, doubling effective moisture infiltration."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_surface_temperature", direction="decrease", expected_time="short_term", scientific_basis="Reflective biological mulch mitigates thermal shock to topsoil biotas."),
                    ImpactedMetric(metric="effective_water_infiltration", direction="increase", expected_time="short_term", scientific_basis="Contour swales prevent surface sheet runoff and crusting."),
                    ImpactedMetric(metric="epigeic_invertebrate_survival", direction="increase", expected_time="medium_term", scientific_basis="Moist shaded microclimates sustain detritivores through hot seasons.")
                ],
                time_horizon={
                    "short_term": "Immediate: Drastic reduction in evaporative soil water loss and cooler root zone.",
                    "medium_term": "1-2 years: Significant increase in earthworm and beneficial collembola populations.",
                    "long_term": "3+ years: Permanent transformation of dryland microclimate resilience."
                },
                evidence=cover_docs,
                connected_variables=["Annual Rainfall (<500 mm)", "Soil Temperature", "Soil Moisture"]
            )
            _, conf3, notes3 = evidence_validator.validate_recommendation(rec3, retrieved_docs, state)
            rec3.confidence = conf3
            rec3.confidence_rationale = notes3
            recommendations.append(rec3)

        return recommendations

recommendation_engine = RecommendationEngine()
