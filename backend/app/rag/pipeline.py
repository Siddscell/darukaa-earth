"""
RAG Pipeline: orchestrates document retrieval, ranking, and evidence assembly.
"""
import logging
from typing import Optional
from app.services.retriever import Retriever
from app.services.evidence_ranker import rank_evidence
from app.services.citation_builder import build_citations
from app.reasoning.reasoning_engine import generate_reasoning_chain

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self):
        self.retriever = Retriever()

    def run(
        self,
        query: str,
        env_profile: dict,
        active_variables: Optional[list[str]] = None,
    ) -> dict:
        """
        Full RAG pipeline:
        1. Build retrieval query from user query + profile context
        2. Retrieve from ChromaDB (multi-topic for broader coverage)
        3. Rank by composite score
        4. Return ranked evidence list

        Returns:
            {
                "retrieved_docs": [...],
                "ranked_docs": [...],
                "query_used": str,
                "evidence_count": int,
            }
        """
        # Build an enriched query from the profile
        enriched_query = self._build_enriched_query(query, env_profile)

        # Determine relevant topics from the profile
        topics = self._detect_relevant_topics(env_profile, active_variables)

        # Multi-topic retrieval for comprehensive coverage
        if len(topics) > 1:
            retrieved_docs = self.retriever.retrieve_multi_topic(
                enriched_query, topics, n_per_topic=3
            )
            # Also do a general search for additional coverage
            general_docs = self.retriever.retrieve(enriched_query, n_results=3)
            # Merge, dedup
            seen_ids = {d["id"] for d in retrieved_docs}
            for d in general_docs:
                if d["id"] not in seen_ids:
                    retrieved_docs.append(d)
                    seen_ids.add(d["id"])
        else:
            retrieved_docs = self.retriever.retrieve(
                enriched_query, env_profile=env_profile, n_results=8
            )

        # Rank documents
        ranked_docs = rank_evidence(
            retrieved_docs,
            profile=env_profile,
            active_variables=active_variables,
            n_top=6,
        )

        logger.info(
            f"RAG pipeline: retrieved {len(retrieved_docs)} docs, "
            f"ranked to {len(ranked_docs)}"
        )

        return {
            "retrieved_docs": retrieved_docs,
            "ranked_docs": ranked_docs,
            "query_used": enriched_query,
            "evidence_count": len(ranked_docs),
        }

    def _build_enriched_query(self, query: str, profile: dict) -> str:
        """Add key profile terms to the query for better embedding match."""
        terms = [query]

        soil = profile.get("soil") or {}
        if soc := soil.get("organic_carbon_percent"):
            terms.append(f"soil organic carbon {soc}%")
        if ph := soil.get("ph"):
            terms.append(f"soil pH {ph}")

        climate = profile.get("climate") or {}
        if rainfall := climate.get("rainfall_pattern"):
            terms.append(f"{rainfall} rainfall")
        if temp := climate.get("temperature_c"):
            terms.append(f"temperature {temp}C")

        lu = profile.get("land_use") or {}
        if crop := lu.get("crop"):
            terms.append(crop)
        if system := lu.get("cropping_system"):
            terms.append(system)

        hi = profile.get("human_impact") or {}
        if pest := hi.get("pesticide_pressure"):
            terms.append(f"{pest} pesticide")
        if defor := hi.get("deforestation_pressure"):
            if defor == "high":
                terms.append("deforestation")

        return " ".join(terms[:8])  # keep query reasonable length

    def _detect_relevant_topics(
        self, profile: dict, active_variables: Optional[list[str]] = None
    ) -> list[str]:
        """Determine which topics to query based on profile content."""
        topics = []

        soil = profile.get("soil") or {}
        if any(v for v in soil.values() if v is not None):
            topics.append("soil")

        lu = profile.get("land_use") or {}
        if any(v for v in lu.values() if v is not None):
            topics.append("land_use")

        bd = profile.get("biodiversity") or {}
        if any(v for v in bd.values() if v is not None):
            topics.append("biodiversity")

        cl = profile.get("climate") or {}
        if any(v for v in cl.values() if v is not None):
            topics.append("climate")

        hi = profile.get("human_impact") or {}
        if any(v for v in hi.values() if v is not None):
            topics.append("human_impact")

        # Always include biodiversity for agroforestry coverage
        if not topics:
            topics = ["soil", "biodiversity", "land_use"]

        if "soil" in topics and "land_use" in topics:
            topics.append("agroforestry")

        return list(dict.fromkeys(topics))  # deduplicate, preserve order
