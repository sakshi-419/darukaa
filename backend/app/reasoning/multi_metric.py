from typing import List, Dict, Any
from backend.app.schemas.environmental import EnvironmentalState

class EcologicalCausalChain:
    def __init__(self, name: str, variables: List[str], description: str, steps: List[str]):
        self.name = name
        self.variables = variables
        self.description = description
        self.steps = steps

class MultiMetricReasoningEngine:
    """
    Core reasoning layer: models multi-variable interactions across
    Soil Health, Climate Stress, Land Cover, and Human Pressure.
    Strictly uses current inputs and avoids unsupported quantitative claims.
    """
    def reason(self, state: EnvironmentalState) -> Dict[str, Any]:
        s = state.soil
        c = state.climate
        l = state.land
        b = state.biodiversity
        h = state.human_impact

        variables_considered: List[str] = []
        identified_chains: List[EcologicalCausalChain] = []
        diagnostic_insights: List[str] = []

        # Track verified active variables strictly from current state
        if s.organic_carbon_percent is not None:
            variables_considered.append(f"Soil Organic Carbon ({s.organic_carbon_percent}%)")
        if s.ph is not None:
            variables_considered.append(f"Soil pH ({s.ph})")
        if s.moisture_percent is not None:
            variables_considered.append(f"Soil Moisture ({s.moisture_percent}%)")
        if c.annual_rainfall_mm is not None:
            variables_considered.append(f"Annual Rainfall ({c.annual_rainfall_mm} mm)")
        if c.temperature_c is not None:
            variables_considered.append(f"Temperature ({c.temperature_c}°C)")
        if l.land_use:
            variables_considered.append(f"Land Use ({l.land_use})")
        if l.crop:
            variables_considered.append(f"Crop ({l.crop})")
        if l.cropping_system:
            variables_considered.append(f"Cropping System ({l.cropping_system})")
        if h.pesticide_pressure:
            variables_considered.append(f"Pesticide Pressure ({h.pesticide_pressure})")

        # Current crop and management descriptors
        crop_display = l.crop if l.crop else "cultivated crop"
        is_monoculture = (l.cropping_system == "monoculture")
        is_rotation = (l.cropping_system in ["crop rotation", "rotation", "rotational"])
        is_low_soc = s.organic_carbon_percent is not None and s.organic_carbon_percent < 0.75
        is_low_rain = (c.annual_rainfall_mm is not None and c.annual_rainfall_mm < 600) or c.drought_risk == "high"
        is_alkaline = s.ph is not None and s.ph >= 7.5

        # Causal Chain 1: Soil Carbon & Moisture Constraints
        if is_low_soc and is_low_rain:
            if is_rotation:
                chain = EcologicalCausalChain(
                    name="Rotational Cropping Carbon-Moisture Equilibrium",
                    variables=["Rainfall Dynamics", "Soil Organic Carbon", "Rotational Management"],
                    description=(
                        f"In semi-arid conditions ({c.annual_rainfall_mm or 'unrecorded'} mm rainfall), practicing crop rotation with {crop_display} "
                        f"helps moderate disease and nutrient depletion. However, soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) "
                        f"remains a primary constraint for optimizing water-use efficiency."
                    ),
                    steps=[
                        f"Semi-arid moisture regime ({c.annual_rainfall_mm or 'moderate'} mm rainfall) constrains seasonal biomass production",
                        f"Established crop rotation sequence with {crop_display}",
                        f"Soil organic carbon level ({s.organic_carbon_percent or 'unrecorded'}%) governs soil aggregate stability and biological energy",
                        "Maintaining surface residue and diverse root exudates can support soil biological activity and moisture retention"
                    ]
                )
                identified_chains.append(chain)
                diagnostic_insights.append(
                    f"Current management establishes {crop_display} within a crop rotation system. "
                    f"In this moisture regime ({c.annual_rainfall_mm or 'unrecorded'} mm), soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) "
                    f"is the key leverage point to improve rainfall-use efficiency and support soil biological resilience."
                )
            elif is_monoculture:
                chain = EcologicalCausalChain(
                    name="Dryland Monoculture Carbon-Moisture Deficit",
                    variables=["Annual Rainfall (<600 mm)", "Soil Organic Carbon", "Continuous Monoculture"],
                    description=(
                        f"Continuous single-crop cultivation of {crop_display} under limited rainfall ({c.annual_rainfall_mm or 'unrecorded'} mm) "
                        f"interacts with low soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) to restrict biological activity and moisture retention."
                    ),
                    steps=[
                        f"Limited precipitation ({c.annual_rainfall_mm or 'low'} mm) restricts vegetative biomass generation",
                        f"Continuous {crop_display} monoculture without rotational diversity",
                        f"Depleted soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%)",
                        "May diminish soil aggregate stability and moisture retention capacity",
                        "Can reduce microbial habitat diversity and overall agroecosystem buffering capacity"
                    ]
                )
                identified_chains.append(chain)
                diagnostic_insights.append(
                    f"Your assessment indicates continuous {crop_display} monoculture under constrained precipitation "
                    f"({c.annual_rainfall_mm or 'unrecorded'} mm) and low organic carbon ({s.organic_carbon_percent or 'unrecorded'}%), "
                    f"which can restrict soil microbial resilience and moisture buffering."
                )
            else:
                # Cropping system not specified as monoculture or rotation
                chain = EcologicalCausalChain(
                    name="Dryland Soil Organic Carbon and Hydrological Dynamics",
                    variables=["Rainfall Availability", "Soil Organic Carbon", "Cultivated Field Management"],
                    description=(
                        f"The interaction between precipitation ({c.annual_rainfall_mm or 'unrecorded'} mm) and organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) "
                        f"governs soil structure and moisture availability for {crop_display}."
                    ),
                    steps=[
                        f"Seasonal precipitation availability ({c.annual_rainfall_mm or 'unrecorded'} mm)",
                        f"Soil organic carbon reserves ({s.organic_carbon_percent or 'unrecorded'}%)",
                        "Regulates biological energy flux and moisture infiltration in the root zone",
                        "Organic matter management can contribute to sustained crop and biological productivity"
                    ]
                )
                identified_chains.append(chain)
                diagnostic_insights.append(
                    f"Diagnostic modeling shows that for {crop_display}, available precipitation ({c.annual_rainfall_mm or 'unrecorded'} mm) "
                    f"and soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) interact to define the soil moisture buffering capacity."
                )

        # Causal Chain 2: Alkaline Soil Dynamic
        if is_alkaline:
            chain = EcologicalCausalChain(
                name="Alkaline Soil Nutrient and Microbial Dynamic",
                variables=["Soil pH (Alkaline)", "Bioavailability", "Root Exudates"],
                description=(
                    f"Soil pH of {s.ph} creates alkaline conditions that can chemically bind phosphorus and micronutrients, "
                    f"influencing rhizosphere microbial associations."
                ),
                steps=[
                    f"Alkaline soil pH ({s.ph}) tends to complex phosphorus with calcium in semi-arid soils",
                    "Can restrict bioavailable micronutrients for crop and beneficial rhizosphere microorganisms",
                    "Organic matter additions release weak organic acids that can mobilize bound nutrients"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                f"Alkaline soil pH ({s.ph}) is a key biochemical factor that can limit phosphorus and micronutrient availability."
            )

        # Causal Chain 3: Chemical Pressure (ONLY if explicitly indicated)
        if h.pesticide_pressure in ["high", "intensive"]:
            chain = EcologicalCausalChain(
                name="Agricultural Chemical Pressure and Beneficial Invertebrates",
                variables=["Pesticide Pressure", "Beneficial Insects", "Biological Corridors"],
                description="Elevated chemical applications can reduce populations of non-target beneficial insects, detritivores, and pollinators.",
                steps=[
                    "High synthetic pesticide pressure reported in field management",
                    "Can adversely affect non-target predatory beetles, parasitoid wasps, and wild pollinators",
                    "Habitat buffers and integrated pest management can support natural pest control equilibria"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                "Reported high pesticide pressure poses a direct stress on non-target beneficial insect populations and soil biological activity."
            )

        # Fallback chain if no specific trigger, using strictly known current variables
        if not identified_chains:
            known_vars = []
            if s.organic_carbon_percent is not None: known_vars.append(f"SOC {s.organic_carbon_percent}%")
            if c.annual_rainfall_mm is not None: known_vars.append(f"Rainfall {c.annual_rainfall_mm} mm")
            if s.ph is not None: known_vars.append(f"pH {s.ph}")
            if l.crop: known_vars.append(f"Crop {l.crop}")
            if l.cropping_system: known_vars.append(f"Management {l.cropping_system}")
            
            chain = EcologicalCausalChain(
                name="Agroecosystem Ecological Diagnostic",
                variables=known_vars if known_vars else ["Environmental Baseline"],
                description="Evaluation of current site parameters and their ecological interactions.",
                steps=[
                    f"Current crop: {crop_display}",
                    f"Management system: {l.cropping_system or 'unspecified'}",
                    f"Hydrological and edaphic status based on available inputs ({', '.join(known_vars) if known_vars else 'baseline'})"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                f"Multi-metric evaluation based on current inputs for {crop_display}: "
                f"{', '.join(known_vars) if known_vars else 'baseline metrics'}."
            )

        # Build formatted causal pathways
        causal_pathways = []
        for ch in identified_chains:
            causal_pathways.append(f"**{ch.name}**:\n" + " → ".join(ch.steps))

        overall_diagnosis = " ".join(diagnostic_insights)

        return {
            "variables_considered": variables_considered,
            "connected_variable_count": len(variables_considered),
            "identified_chains": identified_chains,
            "causal_pathways": causal_pathways,
            "overall_diagnosis": overall_diagnosis
        }

reasoning_engine = MultiMetricReasoningEngine()
