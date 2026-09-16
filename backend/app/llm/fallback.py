"""
Deterministic fallback reasoning mode.
Used when Ollama is unavailable. Never pretends to be an LLM.
Uses actual retrieved evidence records from ChromaDB.
"""
from typing import Optional
from app.schemas.chat import RecommendationItem, EvidenceItem


def generate_fallback_recommendations(
    reasoning_result: dict,
    retrieved_evidence: list[dict],
) -> list[RecommendationItem]:
    """
    Produce structured recommendations using deterministic template logic
    backed by actually retrieved evidence records.
    
    This is NOT a language model. It assembles structured output
    from the reasoning engine and retrieved evidence.
    """
    intervention_details = reasoning_result.get("intervention_details", [])
    recommendations: list[RecommendationItem] = []

    for intervention in intervention_details:
        # Build evidence items from retrieved docs
        evidence_items = _match_evidence_to_intervention(
            intervention, retrieved_evidence
        )

        if not evidence_items:
            # Use at least one generic evidence item if retrieval returned nothing
            evidence_items = [
                EvidenceItem(
                    title="Environmental Science Baseline Knowledge",
                    source="Scientific consensus (no specific paper retrieved)",
                    year=None,
                    url=None,
                    supporting_excerpt=(
                        "This recommendation reflects widely established principles "
                        "in agroecology and environmental science. No specific document "
                        "was retrieved from the knowledge base for this query. "
                        "Please run knowledge ingestion to improve retrieval quality."
                    ),
                    topic=intervention.get("topic_tags", ["general"])[0],
                    variables=intervention.get("impacted_metrics", []),
                )
            ]

        rec = RecommendationItem(
            title=intervention["title"],
            action=intervention["action"],
            reasoning=intervention["reasoning"],
            impacted_metrics=intervention["impacted_metrics"],
            time_horizon=intervention["time_horizon"],
            confidence=intervention["confidence"],
            evidence=evidence_items,
        )
        recommendations.append(rec)

    return recommendations


def _match_evidence_to_intervention(
    intervention: dict, retrieved_evidence: list[dict]
) -> list[EvidenceItem]:
    """
    Match retrieved evidence records to an intervention based on topic tags
    and variable overlap. Return up to 2 relevant EvidenceItems.
    """
    topic_tags = set(intervention.get("topic_tags", []))
    impacted = set(intervention.get("impacted_metrics", []))
    matched = []

    for doc in retrieved_evidence:
        meta = doc.get("metadata", {})
        doc_topic = meta.get("topic", "")
        doc_vars = set(meta.get("variables", []) or [])
        doc_text = doc.get("text", doc.get("document", ""))

        topic_match = doc_topic in topic_tags
        var_overlap = len(doc_vars & impacted) > 0

        if topic_match or var_overlap:
            # Extract relevant excerpt (first 300 chars of text)
            excerpt = doc_text[:400].strip()
            if len(doc_text) > 400:
                excerpt += "..."

            matched.append(
                EvidenceItem(
                    title=meta.get("title", "Environmental Evidence Record"),
                    source=meta.get("source", "Unknown"),
                    year=_safe_int(meta.get("year")),
                    url=meta.get("url"),
                    supporting_excerpt=excerpt,
                    topic=doc_topic,
                    variables=list(doc_vars),
                )
            )

        if len(matched) >= 2:
            break

    return matched


def generate_clarification_message(questions: list[str]) -> str:
    """Generate a friendly clarification request message."""
    if not questions:
        return "Could you provide more details about your environmental context?"

    intro = (
        "To provide specific, evidence-based recommendations for your situation, "
        "I need a little more information. Could you tell me:"
    )
    lines = [f"\u2022 {q}" for q in questions]
    return intro + "\n\n" + "\n".join(lines)


def generate_summary_message(
    profile: dict,
    reasoning_result: dict,
    recommendations: list[RecommendationItem],
) -> str:
    """
    Generate a concise introductory message for the response,
    summarizing what was detected and what is being recommended.
    """
    active_vars = reasoning_result.get("active_variables", [])
    region = profile.get("region", "your area")
    n_recs = len(recommendations)

    if not active_vars:
        return (
            f"Based on the environmental information you've provided about {region}, "
            f"here are {n_recs} recommendation(s) grounded in the available evidence."
        )

    # Build a summary of detected conditions
    condition_labels = {
        "soil_organic_carbon": "low soil organic carbon",
        "rainfall": "low rainfall",
        "monoculture": "monoculture farming",
        "land_use_intensity": "high land use intensity",
        "habitat_fragmentation": "habitat fragmentation",
        "deforestation": "deforestation pressure",
        "pesticide_pressure": "pesticide pressure",
        "temperature": "elevated temperature",
    }

    conditions = [condition_labels.get(v, v.replace("_", " ")) for v in active_vars[:3]]
    condition_str = ", ".join(conditions)

    chain = reasoning_result.get("relationship_chain", [])
    chain_preview = ""
    if chain:
        chain_preview = (
            f" The key environmental relationships identified are: "
            f"{'; '.join(chain[:3])}."
        )

    return (
        f"Based on your environmental profile for {region}, I identified "
        f"{len(active_vars)} interacting stressor(s): {condition_str}.{chain_preview} "
        f"Here are {n_recs} evidence-grounded recommendation(s) that address these linked factors:"
    )


def _safe_int(val) -> Optional[int]:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


DEMO_MODE_NOTICE = (
    "\u26a0\ufe0f Demo reasoning mode \u2014 Ollama LLM is not available. "
    "Recommendations are generated by a deterministic reasoning engine "
    "using retrieved evidence records, not a language model."
)
