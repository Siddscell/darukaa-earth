"""
Evidence ranker: score retrieved documents by multiple factors and return top N.
"""
from typing import Optional


# Source quality weights
SOURCE_QUALITY = {
    "FAO": 1.0,
    "IPBES": 1.0,
    "IPCC": 1.0,
    "IUCN": 0.95,
    "CIFOR": 0.9,
    "CGIAR": 0.9,
    "ICRISAT": 0.9,
    "ICAR": 0.85,
    "WWF": 0.8,
    "NRCS-USDA": 0.85,
    "EPA": 0.85,
    "Natural England": 0.8,
    "TNC": 0.8,
    "The Nature Conservancy": 0.8,
    "EFSA": 0.85,
    "SARE": 0.75,
    "Rodale Institute": 0.7,
    "IPES-Food": 0.75,
    "Nature Microbiology": 0.85,
    "IUCN Asia": 0.9,
}

TOPIC_SCORE = {
    "soil": 0.9,
    "biodiversity": 0.9,
    "land_use": 0.85,
    "climate": 0.85,
    "human_impact": 0.85,
    "agroforestry": 0.9,
}


def _source_quality_score(source: str) -> float:
    for key, score in SOURCE_QUALITY.items():
        if key.lower() in source.lower():
            return score
    return 0.6


def _topic_score(topic: str) -> float:
    return TOPIC_SCORE.get(topic, 0.7)


def _variable_overlap_score(
    doc_variables: list[str], profile_active_variables: list[str]
) -> float:
    if not doc_variables or not profile_active_variables:
        return 0.0
    doc_set = {v.lower().replace("_", "") for v in doc_variables}
    active_set = {v.lower().replace("_", "") for v in profile_active_variables}
    overlap = len(doc_set & active_set)
    return min(1.0, overlap / max(len(active_set), 1))


def rank_evidence(
    retrieved_docs: list[dict],
    profile: Optional[dict] = None,
    active_variables: Optional[list[str]] = None,
    n_top: int = 6,
) -> list[dict]:
    """
    Score and rank retrieved documents by:
    - Semantic similarity score (from ChromaDB)
    - Source quality
    - Topic relevance
    - Variable overlap with active profile conditions
    
    Returns top N documents sorted by composite score.
    """
    if not retrieved_docs:
        return []

    active_vars = active_variables or []

    scored = []
    for doc in retrieved_docs:
        meta = doc.get("metadata", {})
        source = meta.get("source", "")
        topic = meta.get("topic", "")
        variables = meta.get("variables", []) or []

        # Semantic similarity: normalize ChromaDB distance (lower = better)
        # ChromaDB returns distances; convert to similarity
        distance = doc.get("distance", 0.5)
        semantic_score = max(0.0, 1.0 - distance)

        sq = _source_quality_score(source)
        tq = _topic_score(topic)
        vq = _variable_overlap_score(variables, active_vars)

        # Weighted composite score
        composite = (
            0.4 * semantic_score
            + 0.25 * sq
            + 0.2 * tq
            + 0.15 * vq
        )

        scored.append({**doc, "_score": composite})

    scored.sort(key=lambda x: x["_score"], reverse=True)
    return scored[:n_top]
