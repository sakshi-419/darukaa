from typing import List, Dict, Any, Optional
from backend.app.rag.vector_store import vector_store
from backend.app.schemas.environmental import EnvironmentalState

class RAGRetriever:
    """
    Multi-aspect environmental RAG retriever:
    Generates multi-variable semantic search combinations, queries vector database,
    and reranks evidence documents based on relevance and authoritative credentials.
    Dynamically aligns with the current crop and cropping system.
    """
    def generate_subqueries(self, query: str, state: Optional[EnvironmentalState] = None) -> List[str]:
        subqueries = [query]
        
        # Multi-dimensional environmental expansion strictly from current state
        if state:
            s = state.soil
            c = state.climate
            l = state.land
            h = state.human_impact
            
            # 1. Low organic carbon combinations
            if s.organic_carbon_percent is not None and s.organic_carbon_percent < 0.75:
                subqueries.append("soil organic carbon depletion and microbial diversity recovery")
                subqueries.append("organic amendments humic substances dryland soil moisture retention")
                
            # 2. Moisture / Drought combinations
            if (c.annual_rainfall_mm is not None and c.annual_rainfall_mm < 600) or (s.moisture_percent is not None and s.moisture_percent < 20):
                subqueries.append("drought stress biodiversity resilience soil moisture conservation")
                subqueries.append("dryland agriculture mulch cover crop evaporation reduction")
                
            # 3. Dynamic Management / Crop combinations
            crop_kw = l.crop if l.crop else "crop"
            if l.cropping_system in ["crop rotation", "rotation", "rotational"]:
                subqueries.append(f"optimizing {crop_kw} rotation residue retention soil organic carbon")
                subqueries.append("cover crop rotation biological diversity soil structure")
            elif l.cropping_system == "monoculture":
                subqueries.append(f"diversifying {crop_kw} monoculture legume intercropping rotation")
                subqueries.append("monoculture diversification pest suppression soil health")
            elif l.crop in ["chickpea", "pigeonpea", "lentil", "legumes", "pulses"]:
                subqueries.append(f"{l.crop} nitrogen fixation Rhizobium soil carbon residue")
            elif l.crop:
                subqueries.append(f"{l.crop} agroecological management soil organic carbon moisture")
                
            # 4. Alkaline pH combinations
            if s.ph is not None and s.ph >= 7.5:
                subqueries.append("alkaline soil phosphorus availability organic amendments microbial inoculants")

            # 5. Habitat fragmentation & tree planting
            if l.habitat_fragmentation == "high" or "tree" in query.lower():
                subqueries.append("landscape connectivity hedgerows biological corridors agroforestry")
                subqueries.append("tree planting scientific factors biome suitability native diversity")
                
            # 6. Pesticide pressure (only if explicitly reported)
            if h.pesticide_pressure in ["high", "intensive"]:
                subqueries.append("pesticide reduction integrated pest management beneficial insects earthworms")

        # Fallback multi-dimensional query expansion based on text
        q_lower = query.lower()
        if "dry" in q_lower or "rain" in q_lower or "water" in q_lower:
            subqueries.append("drought and biodiversity soil moisture species survival")
            subqueries.append("dryland agriculture biodiversity resilience")
        if "soil" in q_lower or "carbon" in q_lower:
            subqueries.append("soil organic carbon and microbial diversity respiration")
        if "crop rotation" in q_lower or "rotation" in q_lower:
            subqueries.append("crop rotation residue retention soil biodiversity")
        elif "chickpea" in q_lower or "pulse" in q_lower or "legume" in q_lower:
            subqueries.append("legume pulse soil health nodulation rotation")
        elif "wheat" in q_lower:
            subqueries.append("wheat cropping system soil organic carbon")
        if "tree" in q_lower:
            subqueries.append("tree planting risks percentage biodiversity scientific factors")

        # Ensure unique queries
        return list(dict.fromkeys(subqueries))

    def retrieve_evidence(self, query: str, state: Optional[EnvironmentalState] = None, top_k: int = 4) -> List[Dict[str, Any]]:
        subqueries = self.generate_subqueries(query, state)
        
        # Collect and score documents across all subqueries
        doc_scores: Dict[str, Dict[str, Any]] = {}
        for sq in subqueries:
            results = vector_store.search(sq, top_k=top_k)
            for r in results:
                doc_id = r["id"]
                score = r.get("score", 0.5)
                # Unpack metadata into top-level for direct access (e.g. h["organization"], h["title"])
                meta = r.get("metadata", {})
                merged = {**meta, **r}
                # Authority credential boost
                org = merged.get("organization", "").upper()
                if org in ["IPBES", "FAO", "IPCC", "UNEP"]:
                    score += 0.15
                elif org in ["ICAR", "CGIAR", "SCIENCE"]:
                    score += 0.10

                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {**merged, "final_score": score, "matched_queries": [sq]}
                else:
                    doc_scores[doc_id]["final_score"] = max(doc_scores[doc_id]["final_score"], score)
                    doc_scores[doc_id]["matched_queries"].append(sq)

        # Rerank strictly by final_score descending
        ranked_docs = sorted(doc_scores.values(), key=lambda d: d["final_score"], reverse=True)
        return ranked_docs[:top_k]

rag_retriever = RAGRetriever()
