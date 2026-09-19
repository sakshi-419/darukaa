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
        crop_lower = crop_name.lower()
        system_lower = (l.cropping_system or "").lower()
        land_use_lower = (l.land_use or "").lower()

        is_agroforestry = system_lower == "agroforestry" or land_use_lower == "agroforestry" or "native trees" in crop_lower or "trees" in crop_lower
        is_legume = any(leg in crop_lower for leg in ["chickpea", "pigeonpea", "lentil", "cowpea", "pea", "pulses", "legumes", "soybean", "groundnut"])
        is_rotation = system_lower in ["crop rotation", "rotation", "rotational"]
        is_monoculture = system_lower == "monoculture"

        # -------------------------------------------------------------
        # 1. Cropping System & Agroecosystem Recommendation
        # -------------------------------------------------------------
        if is_agroforestry:
            # User ALREADY has agroforestry established: Optimize it! Do NOT recommend converting to agroforestry.
            agro_docs = find_evidence_for_topic(["agroforestry", "tree", "shade", "biodiversity", "fao", "ipbes"])
            rec1 = BiodiversityRecommendation(
                id="rec_optimize_agroforestry",
                title=f"Optimize Established Agroforestry System with Canopy Pruning and Mulch Cycling",
                action=(
                    f"Manage the existing tree-crop canopy architecture through periodic selective pruning to balance solar radiation "
                    f"for understory {crop_name} while cycling pruned woody and leafy biomass onto the soil surface as protective organic mulch."
                ),
                why_it_works=(
                    "Because agroforestry is already established, active canopy and root management balances light competition with "
                    "tree-mediated microclimate cooling and deep-rooted organic matter turnover, supporting soil resilience under restricted rainfall."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="microclimate_buffering", direction="Potential improvement, depending on canopy density and species", expected_time="short_term", scientific_basis="Tree canopy moderates solar radiation and buffers topsoil temperature extremes."),
                    ImpactedMetric(metric="soil_organic_carbon", direction="Potential increase, depending on pruned biomass return", expected_time="medium_term", scientific_basis="Leaf litter and root exudates provide diverse carbon inputs to the soil profile.")
                ],
                time_horizon={
                    "short_term": "1-3 months: Optimized sunlight transmission to understory crops following pruning.",
                    "medium_term": "1-2 years: Gradual build-up of surface organic mulch layer.",
                    "long_term": "3+ years: Deep root channel formation and sustained microclimate buffering."
                },
                evidence=agro_docs,
                evidence_strength="Strong evidence",
                connected_variables=["Agroforestry", "Canopy Management", "Soil Moisture"]
            )
            recommendations.append(rec1)

        elif is_rotation:
            # User is ALREADY practicing crop rotation: Optimize it! Do NOT recommend converting to rotation.
            rotation_docs = find_evidence_for_topic(["rotation", "cover crop", "residue", "organic", "fao"])
            rec1 = BiodiversityRecommendation(
                id="rec_optimize_rotation_residue",
                title=f"Optimize Existing {crop_name.title()} Rotation with Organic Residue Retention",
                action=(
                    f"Consider retaining post-harvest crop residues on the soil surface where appropriate, "
                    f"with cover crops or green manures evaluated based on seasonal moisture availability and local extension recommendations."
                ),
                why_it_works=(
                    "Because crop rotation is already practiced, maintaining surface residue cover and diversifying rotational windows "
                    "can support soil organic carbon accumulation and moisture retention without disrupting current rotational schedules."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_organic_carbon", direction="Potential increase, depending on biomass inputs and tillage", expected_time="medium_term", scientific_basis="Surface biomass decomposition and root turnover contribute to humic organic reserves."),
                    ImpactedMetric(metric="soil_moisture_retention", direction="Potential improvement, depending on residue cover and soil texture", expected_time="medium_term", scientific_basis="Preserved soil pore architecture and surface shading reduce evaporative loss.")
                ],
                time_horizon={
                    "short_term": "Weeks to months: Reduced surface crusting and shaded topsoil beneath residue mulch.",
                    "medium_term": "1-2 years: Stabilization of soil organic carbon and improved moisture buffering.",
                    "long_term": "3+ years: Self-buffering soil structural resilience and enhanced rainfall-use efficiency."
                },
                evidence=rotation_docs,
                evidence_strength="Strong evidence",
                connected_variables=["Crop Rotation", "Soil Organic Carbon", "Residue Retention"]
            )
            recommendations.append(rec1)

        elif is_monoculture:
            # User is in continuous monoculture: Recommend evaluating diversification
            monoculture_docs = find_evidence_for_topic(["intercropping", "legume", "monoculture", "diversification", "fao"])
            alt_legumes = "legumes (such as chickpea, pigeonpea, or cowpea)" if not is_legume else "cereal and oilseed break crops"
            rec1 = BiodiversityRecommendation(
                id="rec_diversify_monoculture",
                title=f"Evaluate Diversification Options for Continuous {crop_name.title()} Monoculture",
                action=(
                    f"Consider introducing rotational sequences or strip-intercropping with site-adapted break crops "
                    f"such as drought-adapted {alt_legumes}, with specific crop selection guided by local market and agroclimatic conditions."
                ),
                why_it_works=(
                    f"Continuous single-crop cultivation of {crop_name} can restrict root-zone biological diversity. "
                    f"Introducing structured crop rotations disrupts host-specific pest cycles and introduces diverse root exudates "
                    f"that can stimulate beneficial bacterial and mycorrhizal communities."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_organic_carbon", direction="Potential increase, depending on crop species and residue return", expected_time="medium_term", scientific_basis="Multi-species root systems provide diverse organic substrates for carbon stabilization."),
                    ImpactedMetric(metric="natural_pest_predation", direction="Potential improvement, depending on crop sequence", expected_time="medium_term", scientific_basis="Breaks soil-borne monoculture pest and pathogen reservoirs."),
                    ImpactedMetric(metric="soil_moisture_retention", direction="Potential improvement, depending on soil structure", expected_time="medium_term", scientific_basis="Diverse root architectures may enhance infiltration and aggregate stability.")
                ],
                time_horizon={
                    "short_term": "1 season: Interrupted pest cycles and emergence of diverse root exudates.",
                    "medium_term": "1-2 years: Progressive enhancement of active carbon fractions and moisture buffering.",
                    "long_term": "3+ years: Agroecosystem diversification and sustained soil carrying capacity."
                },
                evidence=monoculture_docs,
                evidence_strength="Strong evidence",
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
                    ImpactedMetric(metric="soil_organic_carbon", direction="Potential increase, depending on organic input volume", expected_time="medium_term", scientific_basis="Biomass retention contributes to active and humified organic fractions."),
                    ImpactedMetric(metric="soil_moisture_retention", direction="Potential improvement, depending on mulch cover", expected_time="medium_term", scientific_basis="Enhanced aggregate stability and surface mulch buffer moisture loss.")
                ],
                time_horizon={
                    "short_term": "1-3 months: Shaded topsoil microclimate and reduced moisture evaporation.",
                    "medium_term": "1-2 years: Gradual build-up of organic carbon and biological porosity.",
                    "long_term": "3+ years: Enhanced ecological drought buffering."
                },
                evidence=general_docs,
                evidence_strength="Moderate evidence",
                connected_variables=["Soil Organic Carbon", "Residue Management"]
            )
            recommendations.append(rec1)

        # -------------------------------------------------------------
        # 2. Soil pH & Nutrient Management (Alkaline vs Acidic)
        # -------------------------------------------------------------
        if s.ph is not None and s.ph >= 7.5:
            alkaline_docs = find_evidence_for_topic(["nutrient", "organic amendment", "biofertilizer", "soil"])
            rec2 = BiodiversityRecommendation(
                id="rec_alkaline_nutrient_management",
                title="Soil-Test-Guided Nutrient Management and Organic Amendments for Alkaline Soils",
                action=(
                    "Consider organic amendments (such as well-cured compost or farmyard manure) where appropriate, "
                    "with application rates guided by periodic soil testing to improve nutrient bioavailability in alkaline conditions."
                ),
                why_it_works=(
                    f"At soil pH {s.ph}, chemical availability of phosphorus and zinc can be constrained. "
                    "Composted organic amendments release weak organic acids that may assist in mobilizing bound mineral nutrients, "
                    "though targeted soil testing should verify whether specific nutrient supplementation is needed."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="nutrient_bioavailability", direction="Potential improvement, depending on soil buffering and testing", expected_time="short_term", scientific_basis="Microbial organic acids mobilize chemically bound phosphorus and micronutrients.")
                ],
                time_horizon={
                    "short_term": "1-2 months: Improved root-zone nutrient solubility and early plant vigor.",
                    "medium_term": "1 year: Enhanced biological cycling of phosphorus and micronutrients.",
                    "long_term": "3+ years: Stabilized rhizosphere pH buffering capacity."
                },
                evidence=alkaline_docs,
                evidence_strength="Moderate evidence",
                connected_variables=["Soil pH", "Nutrient Bioavailability", "Organic Amendments"]
            )
            recommendations.append(rec2)

        elif s.ph is not None and s.ph < 6.0:
            acidic_docs = find_evidence_for_topic(["lime", "acidic", "soil health", "ph", "fao"])
            rec2 = BiodiversityRecommendation(
                id="rec_acidic_nutrient_management",
                title="Soil-Test-Guided Nutrient Management and Liming Evaluation for Acidic Soils",
                action=(
                    "Conduct laboratory soil testing to determine exchangeable acidity and base saturation. "
                    "Where indicated by local extension guidelines, evaluate agricultural lime or organic amendments to moderate acidity and improve nutrient availability."
                ),
                why_it_works=(
                    f"In acidic soils (pH {s.ph}), phosphorus availability can be restricted by aluminum or iron binding. "
                    "Soil-test-guided amendments help ensure applications match site-specific buffering capacity."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="nutrient_bioavailability", direction="Potential improvement, depending on lime requirement testing", expected_time="short_term", scientific_basis="Moderating soil acidity reduces aluminum fixation of phosphorus.")
                ],
                time_horizon={
                    "short_term": "1-2 months: Neutralization of free hydrogen/aluminum ions in the topsoil.",
                    "medium_term": "1 season: Improved phosphorus uptake and root elongation.",
                    "long_term": "2-3 years: Normalized cation exchange capacity."
                },
                evidence=acidic_docs,
                evidence_strength="Moderate evidence",
                connected_variables=["Soil pH", "Acidic Soil Management", "Nutrient Bioavailability"]
            )
            recommendations.append(rec2)

        # -------------------------------------------------------------
        # 3. Moisture Conservation & In-situ Catchments (Only in dryland/semi-arid conditions)
        # -------------------------------------------------------------
        is_dryland = ((c.annual_rainfall_mm is not None and c.annual_rainfall_mm <= 650) or
                      (s.moisture_percent is not None and s.moisture_percent <= 20) or
                      (state.location.region and "arid" in state.location.region.lower()))
        is_high_rainfall = c.annual_rainfall_mm is not None and c.annual_rainfall_mm >= 800

        if is_dryland and not is_high_rainfall:
            moisture_docs = find_evidence_for_topic(["water harvesting", "moisture", "mulch", "drought", "ipcc"])
            rec3 = BiodiversityRecommendation(
                id="rec_in_situ_moisture_conservation",
                title="Evaluate In-Situ Soil Moisture Conservation and Surface Mulching",
                action=(
                    "Contour-based moisture conservation measures (such as micro-catchment ridges or furrows) may be considered "
                    "where field slope, soil texture, and rainfall intensity make them appropriate, alongside protective crop residue retention."
                ),
                why_it_works=(
                    "In semi-arid agroecosystems, high surface temperatures drive substantial evaporation from bare soil. "
                    "Organic surface mulch shades the topsoil, which can moderate extreme root-zone temperatures, while contour measures "
                    "slow overland sheet flow, facilitating rainfall infiltration into the active root zone."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="soil_moisture_retention", direction="Potential improvement, depending on mulch thickness and soil texture", expected_time="short_term", scientific_basis="Surface mulch retards direct solar evaporation and buffers root-zone temperatures."),
                    ImpactedMetric(metric="rainfall_use_efficiency", direction="Potential improvement, depending on slope and furrow design", expected_time="short_term", scientific_basis="Contour furrows capture runoff and facilitate localized moisture infiltration.")
                ],
                time_horizon={
                    "short_term": "Immediate: Shading reduces topsoil thermal baking and slows evaporation.",
                    "medium_term": "1 season: Improved crop moisture access during dry intervals.",
                    "long_term": "2-3 years: Sustained biological drought resilience across the field."
                },
                evidence=moisture_docs,
                evidence_strength="Moderate evidence",
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
                title="Consider Native Flowering Vegetative Buffer Strips Along Field Perimeters",
                action=(
                    "Establishing native perennial vegetative buffer strips along field boundaries may be evaluated where field layout and property "
                    "boundaries permit, selecting locally adapted flowering shrubs and bunchgrasses to support beneficial insects."
                ),
                why_it_works=(
                    "Field boundary vegetation provides supplementary floral nectar and pollen for wild pollinators and predatory insects "
                    "during crop fallow phases, supporting natural biological pest regulation while helping filter wind-borne dust."
                ),
                impacted_metrics=[
                    ImpactedMetric(metric="beneficial_insect_abundance", direction="Potential improvement, depending on plant species selection", expected_time="short_term", scientific_basis="Provides season-long floral and nesting resources for wild pollinators and predators."),
                    ImpactedMetric(metric="landscape_habitat_diversity", direction="Potential improvement, depending on boundary connectivity", expected_time="medium_term", scientific_basis="Establishes linear semi-natural corridors connecting agricultural patches.")
                ],
                time_horizon={
                    "short_term": "1-3 months: Early colonization by foraging native pollinators and predatory insects.",
                    "medium_term": "1-2 years: Established perennial nesting sites and biological pest regulation.",
                    "long_term": "3+ years: Semi-natural habitat network supporting field microclimates."
                },
                evidence=buffer_docs,
                evidence_strength="Moderate evidence",
                connected_variables=["Habitat Diversity", "Field Boundaries", "Beneficial Insects"]
            )
            recommendations.append(rec4)

        return recommendations

recommendation_engine = RecommendationEngine()
