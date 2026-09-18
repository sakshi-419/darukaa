from typing import List, Tuple
from backend.app.schemas.environmental import EnvironmentalState, ClarificationQuestion

class ClarifyingQuestionEngine:
    """
    Evaluates missing environmental information based on diagnostic value.
    Prioritizes: Required -> Highly Useful -> Optional.
    Caps questions strictly at 3 to 5 to avoid overwhelming the user.
    """
    def evaluate(self, state: EnvironmentalState, query_text: str = "") -> Tuple[bool, List[ClarificationQuestion]]:
        """
        Returns:
            (is_ready_for_diagnosis: bool, questions: List[ClarificationQuestion])
        """
        s = state.soil
        c = state.climate
        l = state.land
        h = state.human_impact
        
        # Count established key diagnostic variables
        diagnostic_signals = 0
        if s.organic_carbon_percent is not None:
            diagnostic_signals += 1
        if s.ph is not None:
            diagnostic_signals += 1
        if s.moisture_percent is not None:
            diagnostic_signals += 1
        if c.annual_rainfall_mm is not None:
            diagnostic_signals += 1
        if l.crop is not None or l.cropping_system is not None:
            diagnostic_signals += 1
        if l.land_use is not None:
            diagnostic_signals += 1

        # If user explicitly asks a hypothetical or scenario question (e.g. "planting 100 trees"),
        # we can diagnose immediately with contextual parameters!
        if "tree" in query_text.lower() and ("100" in query_text or "plant" in query_text):
            return True, []

        # If at least 3 high-impact environmental variables are present, we have sufficient basis
        # for a multi-metric diagnostic!
        if diagnostic_signals >= 3:
            return True, []

        # Otherwise, identify high-value missing variables in order of diagnostic priority
        questions: List[ClarificationQuestion] = []

        # 1. Soil Organic Carbon (Top biological foundation)
        if s.organic_carbon_percent is None:
            questions.append(ClarificationQuestion(
                field="soil_organic_carbon",
                priority="required",
                question="What is your approximate soil organic carbon percentage (SOC %)?",
                unit_or_format="e.g., 0.3% - 1.5%"
            ))

        # 2. Annual or Seasonal Rainfall
        if c.annual_rainfall_mm is None:
            questions.append(ClarificationQuestion(
                field="rainfall",
                priority="required",
                question="What is your approximate annual or seasonal rainfall?",
                unit_or_format="e.g., 400 mm"
            ))

        # 3. Current Crop or Vegetation Type
        if l.crop is None and l.land_use is None:
            questions.append(ClarificationQuestion(
                field="crop_or_vegetation",
                priority="required",
                question="What is your current crop, vegetation, or land-use type?",
                unit_or_format="e.g., wheat, monoculture cropland, pasture"
            ))

        # 4. Soil pH
        if s.ph is None and len(questions) < 4:
            questions.append(ClarificationQuestion(
                field="soil_ph",
                priority="highly_useful",
                question="What is your soil pH, if known?",
                unit_or_format="e.g., 6.5 - 8.0"
            ))

        # 5. Cropping Pattern / Land Use Practice
        if l.cropping_system is None and len(questions) < 5:
            questions.append(ClarificationQuestion(
                field="cropping_system",
                priority="highly_useful",
                question="Is your land managed as continuous monoculture, crop rotation, or agroforestry?",
                unit_or_format="monoculture / rotation / agroforestry"
            ))

        # 6. Region / Geographic Location (Optional)
        if state.location.region is None and len(questions) < 5:
            questions.append(ClarificationQuestion(
                field="region",
                priority="optional",
                question="Which region or climate zone is your land located in?",
                unit_or_format="e.g., semi-arid, Mediterranean, temperate"
            ))

        # Return capped at 3 to 5 questions
        selected_questions = questions[:5]
        return False, selected_questions

clarification_engine = ClarifyingQuestionEngine()
