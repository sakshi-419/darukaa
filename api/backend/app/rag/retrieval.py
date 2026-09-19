from typing import List, Dict, Any, Optional
from backend.app.rag.vector_store import vector_store
from backend.app.schemas.environmental import EnvironmentalState

class RAGRetriever:
    """
    Multi-aspect environmental RAG retriever:
    Generates multi-variable semantic search combinations, queries vector database,
    and reranks evidence documents based on relevance and authoritative credentials.
    """
    def generate_subqueries(self, query: str, state: Optional[EnvironmentalState] = None) -> List[str]:
        subqueries = [query]
        
        # Multi-dimensional environmental expansion
        if state:
            s = state.soil
            c = state.climate
            l = state.land
            b = state.biodiversity
            h = state.human_impact
            
            # 1. Low organic carbon combinations
            if s.organic_carbon_percent is not None and s.organic_carbon_percent < 0.6:
                subqueries.append("soil organic carbon depletion and microbial diversity recovery")
                subqueries.append("organic amendments humic substances dryland soil moisture retention")
                
            # 2. Moisture / Drought combinations
            if (c.annual_rainfall_mm is not None and c.annual_rainfall_mm < 500) or (s.moisture_percent is not None and s.moisture_percent < 18):
                subqueries.append("drought stress biodiversity resilience soil moisture conservation")
                subqueries.append("dryland agriculture mulch cover crop evaporation reduction")
                
            # 3. Monoculture / Land use combinations
            if l.cropping_system == "monoculture" or l.crop:
                subqueries.append("diversifying cereal monoculture legume intercropping Rhizobium soil health")
                subqueries.append("native vegetative buffer strips beneficial insects pollinator habitat")
                
            # 4. Habitat fragmentation & tree planting
            if l.habitat_fragmentation == "high" or "tree" in query.lower():
                subqueries.append("landscape connectivity hedgerows biological corridors agroforestry")
                subqueries.append("tree planting scientific factors biome suitability native diversity")
                
            # 5. Pesticide pressure
            if h.pesticide_pressure in ["high", "intensive"]:
                subqueries.append("pesticide reduction integrated pest management soil macrofauna earthworms")

        # Fallback multi-dimensional query expansion based on text
        q_lower = query.lower()
        if "dry" in q_lower or "rain" in q_lower or "water" in q_lower:
            subqueries.append("drought and biodiversity soil moisture species survival")
            subqueries.append("dryland agriculture biodiversity resilience")
        if "soil" in q_lower or "carbon" in q_lower:
            subqueries.append("soil organic carbon and microbial diversity respiration")
        if "farm" in q_lower or "crop" in q_lower or "wheat" in q_lower:
            subqueries.append("cereal monoculture crop diversification legume intercrop")
        if "tree" in q_lower:
            subqueries.append("tree planting risks percentage biodiversity scientific factors")

        # Ensure unique queries
        return list(dict.fromkeys(subqueries))

    def retrieve_evidence(self, query: str, state: Optional[EnvironmentalState] = None, top_k: int = 4) -> List[Dict[str, Any]]:
        subqueries = self.generate_subqueries(query, state)
        
        # Collect and score documents across all subqueries
        doc_scores: Dict[str, Dict[str, Any]] = {}
        
        for q in subqueries:
            hits = vector_store.search(q, top_k=3)
            for rank, hit in enumerate(hits):
                doc_id = hit["id"]
                # Reciprocal rank fusion: 1 / (60 + rank) + hit score
                rrf_score = (1.0 / (60.0 + rank)) + (hit["score"] * 0.5)
                
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {
                        "id": doc_id,
                        "title": hit["metadata"].get("title", ""),
                        "authors": hit["metadata"].get("authors", ""),
                        "organization": hit["metadata"].get("organization", ""),
                        "year": int(hit["metadata"].get("year", 2023)),
                        "url": hit["metadata"].get("url", ""),
                        "content": hit["content"],
                        "topic": hit["metadata"].get("topic", "general"),
                        "metrics": hit["metadata"].get("metrics", "").split(",") if hit["metadata"].get("metrics") else [],
                        "total_score": rrf_score,
                        "match_count": 1
                    }
                else:
                    doc_scores[doc_id]["total_score"] += rrf_score
                    doc_scores[doc_id]["match_count"] += 1

        # Rerank by combined score and authoritative institution boost
        ranked = list(doc_scores.values())
        authoritative_orgs = {"FAO", "IPBES", "IPCC", "UNEP", "Science / AAAS", "Nature Geoscience / Peer-Reviewed"}
        for doc in ranked:
            if doc["organization"] in authoritative_orgs:
                doc["total_score"] += 0.15

        ranked.sort(key=lambda x: x["total_score"], reverse=True)
        return ranked[:top_k]

rag_retriever = RAGRetriever()
