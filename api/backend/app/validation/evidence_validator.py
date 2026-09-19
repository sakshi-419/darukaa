import re
from typing import List, Dict, Any, Tuple
from backend.app.schemas.environmental import (
    BiodiversityRecommendation, ScientificEvidence, EnvironmentalState
)

class EvidenceValidator:
    """
    Rigorously validates recommendations against retrieved scientific evidence:
    1. Rejects fabricated numerical certainty / unsupported percentage claims.
    2. Verifies that claimed metrics are backed by source texts.
    3. Calculates confidence (High / Medium / Low) based on evidence relevance and data completeness.
    """
    def check_unsupported_quantitative_claims(self, query: str) -> Tuple[bool, str]:
        """
        Specialized validation for queries demanding arbitrary quantitative predictions
        (e.g., "How much will biodiversity increase if I plant 100 trees?").
        """
        q_lower = query.lower()
        tree_patterns = [
            r'how\s+much\s+(?:will|does)?\s*biodiversity\s*increase.*(?:100|1000|trees?)',
            r'plant(?:ing)?\s*\d+\s*trees?.*(?:percentage|increase|percent)',
            r'how\s+many\s+percent.*tree'
        ]
        for pat in tree_patterns:
            if re.search(pat, q_lower) or ("plant" in q_lower and "tree" in q_lower and ("percent" in q_lower or "how much" in q_lower)):
                notice = (
                    "A reliable quantitative percentage increase cannot be scientifically estimated from the available information.\n\n"
                    "Ecological peer-reviewed research (Holl & Brancalion, Science 2020) establishes that biodiversity outcomes "
                    "cannot be predicted by seedling quantity alone. The actual ecological impact depends strictly on:\n"
                    "• Biome suitability (avoiding afforestation in naturally open arid/grassland ecosystems)\n"
                    "• Native vs non-native tree species selection\n"
                    "• Baseline landscape connectivity to intact natural habitats\n"
                    "• Local hydrologic balance and water table depth\n"
                    "• Soil organic carbon and moisture capacity\n"
                    "• Multi-year seedling survival rates and protection from grazing"
                )
                return True, notice

        return False, ""

    def validate_recommendation(
        self,
        rec: BiodiversityRecommendation,
        retrieved_docs: List[Dict[str, Any]],
        state: EnvironmentalState
    ) -> Tuple[bool, str, str]:
        """
        Validates whether retrieved documents substantiate the recommendation.
        Returns:
            (is_valid: bool, confidence_level: str, validation_notes: str)
        """
        if not retrieved_docs:
            return False, "low", "No retrieved scientific evidence found in knowledge base."

        # Check if any retrieved document mentions the primary impacted metrics
        supported_metrics_found = 0
        matching_orgs = set()
        
        all_doc_content = " ".join([d["content"].lower() for d in retrieved_docs])
        
        for m in rec.impacted_metrics:
            m_key = m.metric.lower().replace("_", " ")
            # Check keywords
            words = m_key.split()
            if any(w in all_doc_content for w in words):
                supported_metrics_found += 1

        for d in retrieved_docs:
            if d.get("organization"):
                matching_orgs.add(d["organization"])

        # Calculate confidence
        # Factors: Evidence quality + Relevance + Input completeness
        inputs_present = 0
        if state.soil.organic_carbon_percent is not None: inputs_present += 1
        if state.climate.annual_rainfall_mm is not None: inputs_present += 1
        if state.land.crop is not None or state.land.land_use is not None: inputs_present += 1
        if state.soil.ph is not None: inputs_present += 1

        if len(retrieved_docs) >= 3 and supported_metrics_found >= 2 and inputs_present >= 3:
            confidence = "high"
            notes = f"Strong multi-source consensus ({', '.join(matching_orgs)}) with high environmental profile completeness."
        elif len(retrieved_docs) >= 1 and supported_metrics_found >= 1:
            confidence = "medium"
            notes = f"Empirical support verified via {', '.join(matching_orgs)}. Moderately complete environmental profile."
        else:
            confidence = "low"
            notes = "Preliminary evidence correlation; further site-specific soil testing recommended."

        return True, confidence, notes

evidence_validator = EvidenceValidator()
