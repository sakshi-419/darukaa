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
    Enforces scientific calibration, uncertainty separation, and grounded inferences.
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

        # 1. Track verified active variables strictly from user inputs (Facts)
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
        if l.crop:
            variables_considered.append(f"Crop / Vegetation ({l.crop})")
        if l.cropping_system:
            variables_considered.append(f"Cropping System ({l.cropping_system})")
        if l.land_use and l.land_use != "cropland":
            variables_considered.append(f"Land Use ({l.land_use})")
        if h.pesticide_pressure:
            variables_considered.append(f"Pesticide Pressure ({h.pesticide_pressure})")

        # Current crop and management descriptors
        crop_display = l.crop if l.crop else "cultivated crop"
        crop_lower = (l.crop or "").lower()
        system_lower = (l.cropping_system or "").lower()
        land_use_lower = (l.land_use or "").lower()

        is_agroforestry = system_lower == "agroforestry" or land_use_lower == "agroforestry" or "native trees" in crop_lower or "trees" in crop_lower
        is_rotation = system_lower in ["crop rotation", "rotation", "rotational"]
        is_monoculture = system_lower == "monoculture"

        # Calibrated SOC categories (never claim "severe collapse" without measurement)
        is_low_soc = s.organic_carbon_percent is not None and s.organic_carbon_percent < 0.50
        is_moderate_soc = s.organic_carbon_percent is not None and 0.50 <= s.organic_carbon_percent <= 0.80
        is_adequate_soc = s.organic_carbon_percent is not None and s.organic_carbon_percent > 0.80

        # Calibrated rainfall categories
        is_low_rain = (c.annual_rainfall_mm is not None and c.annual_rainfall_mm <= 650) or c.drought_risk == "high"
        is_high_rain = (c.annual_rainfall_mm is not None and c.annual_rainfall_mm >= 800)

        # Calibrated pH categories
        is_alkaline = s.ph is not None and s.ph >= 7.5
        is_acidic = s.ph is not None and s.ph < 6.0

        # -------------------------------------------------------------
        # Causal Chain 1: Cropping System & Edaphic-Hydrological Regimes
        # -------------------------------------------------------------
        if is_agroforestry:
            chain = EcologicalCausalChain(
                name="Agroforestry Canopy and Deep-Root Ecological Dynamics",
                variables=["Agroforestry System", "Woody-Perennial Integration", "Moisture Buffering"],
                description=(
                    f"Established agroforestry with {crop_display} provides microclimatic cooling, canopy shading, and deep root turnover "
                    f"that help sustain soil biological activity and moderate evaporative demand under constrained precipitation ({c.annual_rainfall_mm or 'unrecorded'} mm)."
                ),
                steps=[
                    f"Established agroforestry architecture integrating trees with {crop_display}",
                    f"Rainfall availability ({c.annual_rainfall_mm or 'unrecorded'} mm) partitioned between tree and understory root zones",
                    f"Soil organic carbon reserve ({s.organic_carbon_percent or 'unrecorded'}%) provides substrate for beneficial rhizosphere biology",
                    "Periodic canopy pruning and surface litter cycling can balance sunlight interception and conserve topsoil moisture"
                ]
            )
            identified_chains.append(chain)
            soc_desc = f"substantial ({s.organic_carbon_percent}%)" if is_adequate_soc else f"recorded at {s.organic_carbon_percent or 'unrecorded'}%"
            diagnostic_insights.append(
                f"The assessment recognizes an established agroforestry system with {crop_display}. "
                f"Soil organic carbon is {soc_desc}, providing an organic substrate foundation. "
                f"Under limited annual rainfall ({c.annual_rainfall_mm or 'unrecorded'} mm), water availability is an important constraint; "
                f"active canopy management and pruned mulch cycling can help conserve root-zone moisture without excessive light competition."
            )

        elif is_high_rain:
            chain = EcologicalCausalChain(
                name="High-Precipitation Hydrological and Soil Dynamics",
                variables=["Annual Rainfall (>=800 mm)", "Soil Moisture Buffering", "Cropping System"],
                description=(
                    f"In a high-precipitation regime ({c.annual_rainfall_mm} mm) supporting {crop_display}, "
                    f"water availability is abundant. Management focuses on drainage optimization, nutrient retention, "
                    f"and biological soil structure maintenance."
                ),
                steps=[
                    f"Abundant annual rainfall ({c.annual_rainfall_mm} mm) provides ample soil moisture for {crop_display}",
                    f"Cropping management ({l.cropping_system or 'cultivation'}) influences root distribution and soil cover",
                    f"Soil pH of {s.ph or 'unrecorded'} influences nutrient solubility",
                    "Regulated water management and residue retention protect soil aggregates from dispersion"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                f"High annual precipitation ({c.annual_rainfall_mm} mm) and moist soil conditions ({s.moisture_percent or 'unrecorded'}%) "
                f"support {crop_display}, where water deficit is not a primary limiting factor. Drainage and aggregate protection are primary considerations."
            )

        elif is_low_soc and is_monoculture:
            chain = EcologicalCausalChain(
                name="Dryland Monoculture Carbon-Moisture Equilibrium",
                variables=["Annual Rainfall (<650 mm)", "Soil Organic Carbon (<0.5%)", "Continuous Monoculture"],
                description=(
                    f"Continuous single-crop cultivation of {crop_display} under limited rainfall ({c.annual_rainfall_mm or 'unrecorded'} mm) "
                    f"interacts with low soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) to potentially restrict moisture buffering."
                ),
                steps=[
                    f"Constrained precipitation ({c.annual_rainfall_mm or 'low'} mm) limits natural vegetative biomass accumulation",
                    f"Continuous single-crop {crop_display} monoculture without rotational diversity",
                    f"Low soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) may be associated with reduced aggregate stability and water-holding capacity",
                    "Microbial biomass and diversity cannot be inferred from SOC alone and require direct measurement",
                    "Crop diversification and organic residue retention can contribute to improved soil buffering over time"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                f"Your assessment indicates continuous {crop_display} monoculture under constrained precipitation "
                f"({c.annual_rainfall_mm or 'unrecorded'} mm) and low soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%). "
                f"Low SOC may be associated with reduced soil structural stability and lower water-holding capacity. "
                f"However, microbial biomass cannot be inferred from SOC alone and would require direct laboratory measurement."
            )

        elif is_low_soc and is_rotation:
            chain = EcologicalCausalChain(
                name="Rotational Cropping Carbon and Moisture Equilibrium",
                variables=["Rainfall Availability", "Soil Organic Carbon", "Rotational Management"],
                description=(
                    f"In moisture-constrained conditions ({c.annual_rainfall_mm or 'unrecorded'} mm), practicing crop rotation with {crop_display} "
                    f"helps mitigate pest pressures. Maintaining organic residue is a key consideration to build soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%)."
                ),
                steps=[
                    f"Moisture regime ({c.annual_rainfall_mm or 'moderate'} mm) constrains seasonal biomass production",
                    f"Established crop rotation sequence with {crop_display}",
                    f"Low soil organic carbon level ({s.organic_carbon_percent or 'unrecorded'}%) may be associated with lower moisture buffering",
                    "Surface residue retention can contribute to enhanced soil moisture conservation over time"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                f"Current management establishes {crop_display} within an existing crop rotation system. "
                f"In this moisture regime ({c.annual_rainfall_mm or 'unrecorded'} mm), building soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) "
                f"can contribute to improved water-use efficiency and soil biological resilience."
            )

        else:
            # Baseline/general interaction based strictly on current inputs
            chain = EcologicalCausalChain(
                name="Agroecosystem Edaphic and Moisture Dynamics",
                variables=["Precipitation Regime", "Soil Organic Carbon", "Field Management"],
                description=(
                    f"The interaction between rainfall ({c.annual_rainfall_mm or 'unrecorded'} mm) and organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) "
                    f"influences soil moisture buffering and plant vigor for {crop_display}."
                ),
                steps=[
                    f"Seasonal precipitation regime ({c.annual_rainfall_mm or 'unrecorded'} mm)",
                    f"Soil organic carbon level ({s.organic_carbon_percent or 'unrecorded'}%)",
                    f"Management system: {l.cropping_system or 'unspecified'}",
                    "Organic matter management contributes to sustained crop and biological productivity"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                f"For {crop_display} under {l.cropping_system or 'cultivation'}, available precipitation ({c.annual_rainfall_mm or 'unrecorded'} mm) "
                f"and soil organic carbon ({s.organic_carbon_percent or 'unrecorded'}%) interact to define soil moisture buffering capacity."
            )

        # -------------------------------------------------------------
        # Causal Chain 2: Soil pH & Nutrient Bioavailability Dynamics
        # -------------------------------------------------------------
        if is_alkaline:
            chain = EcologicalCausalChain(
                name="Alkaline Soil Nutrient-Availability Dynamics",
                variables=["Soil pH (Alkaline)", "Nutrient Bioavailability", "Root Exudates"],
                description=(
                    f"Soil pH of {s.ph} creates alkaline conditions where chemical fixation of phosphorus and micronutrients (such as zinc) "
                    f"can reduce their plant availability. Soil testing is necessary to confirm actual nutrient status."
                ),
                steps=[
                    f"Alkaline soil pH ({s.ph}) tends to complex phosphorus with calcium and can lower zinc solubility",
                    "May restrict the bioavailability of micronutrients to crops and beneficial rhizosphere organisms",
                    "Soil testing should be conducted to determine whether actual nutrient supplementation or organic amendments are needed"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                f"Alkaline soil pH ({s.ph}) is a key biochemical factor where phosphorus and zinc availability can be reduced due to mineral fixation. "
                f"However, an alkaline pH alone does not prove nutrient deficiency; direct soil testing is required to verify actual nutrient concentrations."
            )

        elif is_acidic:
            chain = EcologicalCausalChain(
                name="Acidic Soil Nutrient-Availability Dynamics",
                variables=["Soil pH (Acidic)", "Base Saturation", "Phosphorus Fixation"],
                description=(
                    f"Soil pH of {s.ph} creates moderately acidic conditions where phosphorus can be bound by iron and aluminum minerals, "
                    f"and base saturation may be constrained."
                ),
                steps=[
                    f"Acidic soil pH ({s.ph}) can promote chemical fixation of phosphorus by iron and aluminum oxides",
                    "May influence root development and microbial nodulation in sensitive crops",
                    "Laboratory soil testing can measure exchangeable acidity to determine whether liming or targeted fertilization is appropriate"
                ]
            )
            identified_chains.append(chain)
            diagnostic_insights.append(
                f"Soil pH ({s.ph}) indicates moderately acidic conditions, which can influence phosphorus availability. "
                f"Standard laboratory soil testing can verify exchangeable acidity and determine if corrective amendments are appropriate."
            )

        # -------------------------------------------------------------
        # Causal Chain 3: Chemical Pressure (ONLY if explicitly indicated)
        # -------------------------------------------------------------
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

        # Build formatted causal pathways
        causal_pathways = []
        for ch in identified_chains:
            causal_pathways.append(f"**{ch.name}**:\n" + " → ".join(ch.steps))

        # Collect unmeasured variables (never invent measurements)
        unmeasured_vars: List[str] = []
        if s.ph is None: unmeasured_vars.append("Soil pH: Not provided")
        if s.moisture_percent is None: unmeasured_vars.append("Soil moisture: Not provided")
        if s.organic_carbon_percent is None: unmeasured_vars.append("Soil organic carbon: Not provided")
        if c.annual_rainfall_mm is None: unmeasured_vars.append("Annual rainfall: Not provided")
        if not l.crop: unmeasured_vars.append("Crop / vegetation: Not provided")
        if not l.cropping_system: unmeasured_vars.append("Management system: Not provided")
        unmeasured_vars.extend([
            "Soil texture: Not provided / unmeasured",
            "Nutrient concentrations (P, Zn, N): Not provided / unmeasured",
            "Microbial biomass & diversity: Not measured directly",
            "Aggregate stability & erosion rate: Not measured",
            "Groundwater level & salinity: Not provided / unmeasured"
        ])

        facts_text = f"**User-Reported Site Inputs:** {', '.join(variables_considered) if variables_considered else 'No quantitative measurements provided.'}"
        inferences_text = f"**Scientific Assessment & Calibrated Inferences:** {' '.join(diagnostic_insights)}"
        uncertainties_text = f"**Unmeasured Variables & Site Uncertainties:** Variables not provided ({', '.join(unmeasured_vars[:4])}) cannot be determined from available data. Specific nutrient concentrations and microbial parameters require on-site laboratory testing."

        overall_diagnosis = f"{facts_text}\n\n{inferences_text}\n\n{uncertainties_text}"

        return {
            "variables_considered": variables_considered,
            "connected_variable_count": len(variables_considered),
            "identified_chains": identified_chains,
            "causal_pathways": causal_pathways,
            "overall_diagnosis": overall_diagnosis,
            "unmeasured_variables": unmeasured_vars
        }

reasoning_engine = MultiMetricReasoningEngine()

