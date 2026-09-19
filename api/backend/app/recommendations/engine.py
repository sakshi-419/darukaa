from typing import List, Dict, Any
from backend.app.schemas.environmental import (
    BiodiversityRecommendation, ImpactedMetric, ScientificEvidence, EnvironmentalState
)

class RecommendationEngine:
    """
    Generates non-obvious, evidence-backed biodiversity interventions
    tailored strictly to the active environmental variables and current management.
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
                meta = doc.get("metadata", {}) if isinstance(doc.get("metadata"), dict) else {}
                title = doc.get("title") or meta.get("title") or doc.get("id", "Scientific Publication")
                org = doc.get("organization") or meta.get("organization") or "FAO / IPBES Scientific Panel"
                authors = doc.get("authors") or meta.get("authors") or "Scientific Research Panel"
                try:
                    year = int(doc.get("year") or meta.get("year") or 2022)
                except Exception:
                    year = 2022
                url = doc.get("url") or meta.get("url") or "https://darukaa.earth/science"
                source_type = doc.get("source_type") or meta.get("source_type") or "report"
                
                raw_metrics = doc.get("metrics") or meta.get("metrics") or []
                if isinstance(raw_metrics, str):
                    metrics_supported = [m.strip() for m in raw_metrics.split(",") if m.strip()]
                elif isinstance(raw_metrics, list):
                    metrics_supported = raw_metrics
                else:
                    metrics_supported = []

                content_lower = (doc.get("content") or "").lower()
                title_lower = title.lower()

                if any(k in content_lower or k in title_lower for k in topic_keywords):
                    matched.append(ScientificEvidence(
                        title=title,
                        organization=org,
                        authors=authors,
                        year=year,
                        url=url,
                        relevance=f"Demonstrates agroecological mechanisms for {', '.join(topic_keywords[:3])}.",
                        source_type=source_type,
                        metrics_supported=metrics_supported
                    ))
            if not matched and retrieved_docs:
                top = retrieved_docs[0]
                meta = top.get("metadata", {}) if isinstance(top.get("metadata"), dict) else {}
                title = top.get("title") or meta.get("title") or top.get("id", "Scientific Framework")
                org = top.get("organization") or meta.get("organization") or "FAO / IPBES Scientific Panel"
                authors = top.get("authors") or meta.get("authors") or "Scientific Research Panel"
                try:
                    year = int(top.get("year") or meta.get("year") or 2022)
                except Exception:
                    year = 2022
                url = top.get("url") or meta.get("url") or "https://darukaa.earth/science"
                source_type = top.get("source_type") or meta.get("source_type") or "report"
                
                raw_metrics = top.get("metrics") or meta.get("metrics") or []
                if isinstance(raw_metrics, str):
                    metrics_supported = [m.strip() for m in raw_metrics.split(",") if m.strip()]
                elif isinstance(raw_metrics, list):
                    metrics_supported = raw_metrics
                else:
                    metrics_supported = []

                matched.append(ScientificEvidence(
                    title=title,
                    organization=org,
                    authors=authors,
                    year=year,
                    url=url,
                    relevance="Provides foundational scientific framework for agroecosystem biodiversity management.",
                    source_type=source_type,
                    metrics_supported=metrics_supported
                ))
            return matched[:2]

        crop_name = l.crop if l.crop else "field crop"
        is_legume = crop_name.lower() in ["chickpea", "pigeonpea", "lentil", "cowpea", "pea", "pulses", "legumes", "soybean", "groundnut"]
        is_rotation = l.cropping_system in ["crop rotation", "rotation", "rotational"]
        is_monoculture = (l.cropping_system == "monoculture")

        # -------------------------------------------------------------
        # 1. Cropping System & Soil Organic Carbon Recommendation
        # -------------------------------------------------------------
        if is_rotation:
            # User is ALREADY practicing crop rotation: Optimize it!
            legume_docs = find_evidence_for_topic(["rotation", "cover crop", "residue", "organic", "fao"])
            rec1 = BiodiversityRecommendation(
                id="rec_optimize_rotation_residue",
                title=f"Optimize Existing {crop_name.title()} Rotation with Organic Residue Retention",
                action=(
                    f"Optimize the established {crop_name} crop rotation by retaining post-harvest crop residues on the soil surface, "
                    f"incorporating site-adapted cover crops or green manures during fallow periods, "
                    f"and minimizing inversion tillage to protect fungal hyphal networks."
                ),
                why_it_works=(
                    "Because crop rotation is already practiced, maintaining surface residue cover and diversifying rotational windows "
                    "can support soil organic carbon accumulation, moderate topsoil temperature extremes, and enhance beneficial rhizosphere "
                    "microbial functional diversity without disrupting current rotational schedules."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_organic_carbon", direction="increase", expected_time="medium_term", scientific_basis="Surface biomass decomposition and root turnover contribute to humic organic reserves."),
                    ImpactedMetric(metric="soil_moisture_retention", direction="increase", expected_time="medium_term", scientific_basis="Preserved soil pore architecture and surface shading reduce evaporative loss."),
                    ImpactedMetric(metric="rhizosphere_microbial_diversity", direction="increase", expected_time="short_term", scientific_basis="Continuous organic inputs nourish diverse heterotrophic bacterial and fungal guilds.")
                ],
                time_horizon={
                    "short_term": "Weeks to months: Reduced surface crusting and enhanced earthworm/microarthropod activity beneath residue mulch.",
                    "medium_term": "1-2 years: Measurable stabilization of soil organic carbon and improved soil moisture dynamics.",
                    "long_term": "3+ years: Self-buffering soil structural resilience and enhanced rainfall-use efficiency."
                },
                evidence=legume_docs,
                connected_variables=["Crop Rotation", "Soil Organic Carbon", "Residue Retention"]
            )
            recommendations.append(rec1)

        elif is_monoculture:
            # User is in continuous monoculture: Recommend diversification
            legume_docs = find_evidence_for_topic(["intercropping", "legume", "monoculture", "diversification", "fao"])
            alt_legumes = "legumes (such as chickpea, pigeonpea, or cowpea)" if not is_legume else "cereal and oilseed break crops"
            rec1 = BiodiversityRecommendation(
                id="rec_diversify_monoculture",
                title=f"Diversify Continuous {crop_name.title()} Monoculture with Rotational Sequences",
                action=(
                    f"Transition continuous {crop_name} monoculture to a diversified rotation or strip-intercropping sequence "
                    f"incorporating drought-adapted {alt_legumes} with post-harvest residue retention."
                ),
                why_it_works=(
                    f"Continuous single-crop cultivation of {crop_name} depletes specific soil nutrient zones and limits biological diversity. "
                    f"Introducing structured crop rotations disrupts host-specific pest cycles and introduces diverse root exudates "
                    f"that can stimulate beneficial bacterial and mycorrhizal communities."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_organic_carbon", direction="increase", expected_time="medium_term", scientific_basis="Multi-species root systems provide diverse organic substrates for carbon stabilization."),
                    ImpactedMetric(metric="natural_pest_predation", direction="increase", expected_time="medium_term", scientific_basis="Breaks soil-borne monoculture pest and pathogen reservoirs."),
                    ImpactedMetric(metric="soil_moisture_retention", direction="increase", expected_time="medium_term", scientific_basis="Improved soil pore geometry and structural aggregate stability retard moisture evaporation.")
                ],
                time_horizon={
                    "short_term": "1 season: Interrupted pest cycles and emergence of beneficial rhizosphere interactions.",
                    "medium_term": "1-2 years: Progressive enhancement of active carbon fractions and moisture buffering.",
                    "long_term": "3+ years: Multi-trophic agroecosystem equilibrium and sustained soil carrying capacity."
                },
                evidence=legume_docs,
                connected_variables=["Monoculture Cropping", "Crop Diversification", "Soil Organic Carbon"]
            )
            recommendations.append(rec1)

        elif (s.organic_carbon_percent is not None and s.organic_carbon_percent < 0.8) or l.crop:
            # Cropping system unspecified: suggest organic residue & cover
            general_docs = find_evidence_for_topic(["organic carbon", "residue", "cover crop", "soil health"])
            rec1 = BiodiversityRecommendation(
                id="rec_soil_organic_enhancement",
                title=f"Enhance {crop_name.title()} Soil Health via Residue Management and Rotational Diversification",
                action=(
                    f"Increase soil organic inputs in {crop_name} fields through systematic crop residue retention, "
                    f"integration of companion green manures where feasible, and reduced tillage intensity."
                ),
                why_it_works=(
                    "Regular organic matter inputs contribute to particulate and mineral-associated organic matter, "
                    "which helps stabilize soil aggregates, supports beneficial decomposers, and improves moisture holding capacity."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_organic_carbon", direction="increase", expected_time="medium_term", scientific_basis="Biomass retention contributes to active and humified organic fractions."),
                    ImpactedMetric(metric="soil_moisture_retention", direction="increase", expected_time="medium_term", scientific_basis="Enhanced aggregate stability and surface mulch buffer moisture loss.")
                ],
                time_horizon={
                    "short_term": "1-3 months: Shaded topsoil microclimate and reduced moisture evaporation.",
                    "medium_term": "1-2 years: Gradual build-up of organic carbon and biological porosity.",
                    "long_term": "3+ years: Enhanced ecological drought buffering."
                },
                evidence=general_docs,
                connected_variables=["Soil Organic Carbon", "Residue Management"]
            )
            recommendations.append(rec1)

        # -------------------------------------------------------------
        # 2. Alkaline Soil & Nutrient Management
        # -------------------------------------------------------------
        if s.ph is not None and s.ph >= 7.5:
            alkaline_docs = find_evidence_for_topic(["nutrient", "organic amendment", "biofertilizer", "soil"])
            rec2 = BiodiversityRecommendation(
                id="rec_alkaline_nutrient_management",
                title="Apply Soil-Test-Based Nutrient Management and Organic Amendments for Alkaline Soils",
                action=(
                    "Apply targeted organic amendments (such as well-cured compost or farmyard manure) combined with "
                    "beneficial bio-inoculants (such as phosphorus-solubilizing bacteria) to buffer alkaline soil pH "
                    "and optimize nutrient bioavailability based on periodic soil testing."
                ),
                why_it_works=(
                    f"At soil pH {s.ph}, chemical fixation of phosphorus and zinc can restrict plant uptake. "
                    "Composted organic amendments release weak organic acids that can mobilize bound mineral nutrients "
                    "in the root zone while fostering beneficial rhizosphere microbial communities without increasing soil salinity."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="nutrient_bioavailability", direction="increase", expected_time="short_term", scientific_basis="Microbial organic acids mobilize chemically fixed phosphorus and micronutrients."),
                    ImpactedMetric(metric="rhizosphere_microbial_activity", direction="increase", expected_time="short_term", scientific_basis="Compost amendments introduce diverse decomposer inocula and metabolic substrates.")
                ],
                time_horizon={
                    "short_term": "1-2 months: Improved root-zone nutrient solubility and early plant vigor.",
                    "medium_term": "1 year: Enhanced biological cycling of phosphorus and micronutrients.",
                    "long_term": "3+ years: Stabilized rhizosphere pH buffering capacity."
                },
                evidence=alkaline_docs,
                connected_variables=["Soil pH", "Nutrient Bioavailability", "Organic Amendments"]
            )
            recommendations.append(rec2)

        # -------------------------------------------------------------
        # 3. Moisture Conservation & In-situ Catchments
        # -------------------------------------------------------------
        if (c.annual_rainfall_mm is not None and c.annual_rainfall_mm <= 650) or (s.moisture_percent is not None and s.moisture_percent <= 20) or (state.location.region and "arid" in state.location.region.lower()):
            moisture_docs = find_evidence_for_topic(["water harvesting", "moisture", "mulch", "drought", "ipcc"])
            rec3 = BiodiversityRecommendation(
                id="rec_in_situ_moisture_conservation",
                title="Implement In-Situ Soil Moisture Conservation and Surface Mulching",
                action=(
                    "Maintain continuous protective soil residue cover (straw or stubble mulching) post-harvest, and construct "
                    "subtle contour furrows or micro-catchment ridges along natural slope contours to guide and retain seasonal rainfall."
                ),
                why_it_works=(
                    "In semi-arid agroecosystems, high surface temperatures drive substantial evaporation from bare soil. "
                    "Organic surface mulch shades the topsoil, which can moderate extreme root-zone temperatures, while contour furrows "
                    "slow overland sheet flow, allowing rainfall to infiltrate into the active root zone."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_moisture_retention", direction="increase", expected_time="short_term", scientific_basis="Surface mulch retards direct solar evaporation and buffers root-zone temperatures."),
                    ImpactedMetric(metric="rainfall_use_efficiency", direction="increase", expected_time="short_term", scientific_basis="Contour furrows capture runoff and facilitate localized moisture infiltration.")
                ],
                time_horizon={
                    "short_term": "Immediate: Shading reduces topsoil thermal baking and slows evaporation.",
                    "medium_term": "1 season: Improved crop moisture access during dry intervals.",
                    "long_term": "2-3 years: Sustained biological drought resilience across the field."
                },
                evidence=moisture_docs,
                connected_variables=["Annual Rainfall", "Soil Moisture", "Surface Temperature"]
            )
            recommendations.append(rec3)

        # -------------------------------------------------------------
        # 4. Vegetative Buffer Strips / Habitat Diversity
        # -------------------------------------------------------------
        if h.pesticide_pressure in ["high", "intensive"] or (l.land_use in ["cropland", "farmland"] and len(recommendations) < 3):
            buffer_docs = find_evidence_for_topic(["buffer", "pollinator", "ipbes", "habitat", "connectivity"])
            rec4 = BiodiversityRecommendation(
                id="rec_native_vegetative_buffers",
                title="Establish Native Flowering Vegetative Buffer Strips Along Field Perimeters",
                action=(
                    "Establish 3 to 5 meter non-crop vegetative buffer zones along field perimeters using locally adapted "
                    "flowering shrubs, perennial bunchgrasses, and pollinator-friendly wildflowers, minimizing pesticide drift into margins."
                ),
                why_it_works=(
                    "Field boundary vegetation provides supplementary floral nectar and pollen for solitary bees, parasitoids, "
                    "and predatory ground beetles during crop fallow phases, supporting natural biological pest regulation "
                    "while helping filter wind-borne dust and surface runoff."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="beneficial_insect_abundance", direction="increase", expected_time="short_term", scientific_basis="Provides season-long floral and nesting resources for wild pollinators and predators."),
                    ImpactedMetric(metric="landscape_habitat_diversity", direction="increase", expected_time="medium_term", scientific_basis="Establishes stable linear corridors connecting isolated agricultural patches.")
                ],
                time_horizon={
                    "short_term": "1-3 months: Rapid colonization by foraging native pollinators and predatory insects.",
                    "medium_term": "1-2 years: Established perennial nesting sites and enhanced biological pest regulation.",
                    "long_term": "3+ years: Resilient semi-natural habitat network supporting field microclimates."
                },
                evidence=buffer_docs,
                connected_variables=["Habitat Diversity", "Field Boundaries", "Beneficial Insects"]
            )
            recommendations.append(rec4)

        return recommendations

recommendation_engine = RecommendationEngine()
