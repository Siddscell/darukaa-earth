"""
Recommendation engine: combine reasoning + evidence + LLM (or fallback)
to produce structured, evidence-grounded RecommendationItems.
"""
import json
import logging
from typing import Optional
from app.schemas.chat import RecommendationItem, EvidenceItem, ReasoningTrace
from app.reasoning.reasoning_engine import generate_reasoning_chain, format_active_variables_for_display
from app.services.citation_builder import build_citations
from app.llm.fallback import (
    generate_fallback_recommendations,
    generate_summary_message,
    generate_clarification_message,
    DEMO_MODE_NOTICE,
)

logger = logging.getLogger(__name__)


# ─── LLM prompt builder ─────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an environmental science assistant generating specific, evidence-grounded intervention recommendations for farmers and land managers.

STRICT RULES — follow every rule exactly:

1. Use ONLY the environmental profile and retrieved evidence provided. Never invent data.
2. Do NOT invent citations, URLs, author names, study titles, or numerical percentages not in the retrieved evidence.
3. If a number (e.g. "increases SOC by 15%") is not in the retrieved evidence, do NOT state it.
4. Each recommendation MUST connect at least two detected environmental stressors. Where evidence supports doing so, explicitly connect at least three relevant factors (e.g., SOC, rainfall, biodiversity).
5. Each recommendation MUST name the exact impacted_metrics (e.g. soil_organic_carbon, water_retention, species_richness).
6. Each recommendation MUST give a realistic time_horizon: short-term (< 1 season), medium-term (1-3 years), or long-term (> 3 years).
7. CONFIDENCE CALIBRATION is critical. Do not automatically assign High:
   - High: Environmental inputs are sufficiently complete, retrieved evidence directly supports the intervention, AND evidence matches the exact local context.
   - Medium: Evidence is relevant but site-specific info (like soil pH or moisture) is missing, the recommendation depends on assumptions, or the evidence is broader than the exact local context.
   - Low: Evidence is weak or indirect.
8. Do NOT use generic phrases such as "use sustainable practices", "improve biodiversity", "adopt sustainable agriculture", or "improve soil health" without a specific mechanism. Be highly specific (e.g., "Introduce a drought-tolerant legume intercrop during the appropriate growing window").
9. CLAIM-TO-EVIDENCE MATCHING: Identify scientific claims in your reasoning and ensure attached evidence supports them. Do not attach unrelated sources just because they discuss agriculture. If an evidence source supports water harvesting, do not treat it as evidence for biodiversity unless explicitly stated in the source text.
10. NO UNSUPPORTED CAUSAL CHAINS: Never invent a causal mechanism (e.g., do not say "better soil moisture causes higher organic matter" unless directly supported by evidence). Prefer conservative wording (e.g., "Water harvesting can increase rainfall retained... Higher SOC can also improve water-holding capacity.").
11. Each recommendation must answer: WHAT exactly to do? WHY (mechanism)? WHICH variables/metrics are affected? HOW LONG?
12. Only cite evidence from the [EVIDENCE] section, using exact titles.
13. Do NOT expose chain-of-thought. Return only concise, practitioner-facing reasoning.
14. Return ONLY valid JSON, no markdown, no extra text.

JSON SCHEMA (return exactly this structure):
{
  "summary_message": "one or two sentences summarising the situation and approach",
  "recommendations": [
    {
      "title": "Short, specific action title",
      "action": "Precise description of what to do — specific crop, timing, method, or technique",
      "reasoning": "Mechanistic explanation: which stressors this addresses, how it works, which variables it affects. Reference the profile values explicitly. Do not invent numbers or causal chains.",
      "impacted_metrics": ["soil_organic_carbon", "water_retention"],
      "time_horizon": "short-term|medium-term|long-term",
      "confidence": "High|Medium|Low",
      "evidence": [
        {
          "title": "Exact title from [EVIDENCE] section",
          "source": "Source from [EVIDENCE] section",
          "year": 2020,
          "url": "URL from [EVIDENCE] section or null",
          "supporting_excerpt": "Brief paraphrase from evidence text directly supporting the claim, do not invent",
          "topic": "topic from [EVIDENCE] section",
          "variables": ["variable from evidence metadata"]
        }
      ]
    }
  ]
}
"""


def _build_user_prompt(
    profile: dict,
    reasoning_result: dict,
    ranked_docs: list[dict],
    user_query: str,
) -> str:
    """Build a rich LLM user prompt with profile values, stressor context, and evidence."""
    profile_str = json.dumps(
        {k: v for k, v in profile.items() if v}, indent=2
    )

    chain = reasoning_result.get("relationship_chain", [])
    active_vars = reasoning_result.get("active_variables", [])
    interventions = reasoning_result.get("interventions", [])

    soc = profile.get("soil", {}).get("organic_carbon_percent", "unknown")
    rainfall = profile.get("climate", {}).get("rainfall_pattern", "unknown")
    crop = profile.get("land_use", {}).get("crop", "unknown")
    region = profile.get("region", "unknown")

    var_labels = {
        "soil_organic_carbon": f"Low soil organic carbon ({soc}%) — reduces water retention and microbial activity",
        "rainfall": f"Low rainfall pattern — creates persistent water and drought stress",
        "monoculture": "Monoculture cropping — reduces habitat diversity and soil microbial diversity",
        "biodiversity_decline": "Biodiversity decline — low species richness and/or habitat diversity detected",
        "deforestation": "Deforestation pressure",
        "habitat_fragmentation": "Habitat fragmentation — impairs ecological connectivity",
        "pesticide_pressure": "Pesticide pressure — affects soil biology and pollinators",
        "temperature": "Elevated temperature stress",
        "land_use_intensity": "High land use intensity",
    }
    stressor_lines = "\n".join(
        f"  - {var_labels.get(v, v.replace('_', ' ').title())}"
        for v in active_vars
    )

    relationship_lines = "\n".join(f"  - {r}" for r in chain)
    suggested = ", ".join(interventions) if interventions else "see evidence"

    evidence_str = ""
    for i, doc in enumerate(ranked_docs[:6]):
        meta = doc.get("metadata", {})
        text = doc.get("text", "")[:700]
        evidence_str += (
            f"\n[Evidence {i+1}]\n"
            f"Title: {meta.get('title', 'Unknown')}\n"
            f"Source: {meta.get('source', 'Unknown')}\n"
            f"Year: {meta.get('year', 'N/A')}\n"
            f"URL: {meta.get('url', 'N/A')}\n"
            f"Topic: {meta.get('topic', 'general')}\n"
            f"Variables: {meta.get('variables', [])}\n"
            f"Text: {text}\n"
        )

    return f"""[USER QUERY]
{user_query}

[ENVIRONMENTAL PROFILE — use these exact values in your reasoning]
{profile_str}

[DETECTED ENVIRONMENTAL STRESSORS]
{stressor_lines}

[ENVIRONMENTAL RELATIONSHIP GRAPH — mechanistic connections between stressors]
{relationship_lines}

[SUGGESTED INTERVENTION TYPES — be specific, not generic]
{suggested}

[RETRIEVED EVIDENCE — cite ONLY from this list using exact titles]
{evidence_str}

TASK: Generate 2-3 specific, evidence-grounded recommendations for this profile.
- Be specific to the profile: SOC={soc}%, rainfall={rainfall}, crop={crop}, region={region}.
- Connect at least two detected stressors per recommendation.
- Cite only evidence from [RETRIEVED EVIDENCE] by exact title.
- Do not invent numbers, citations, or studies.
- Return only valid JSON matching the required schema.
"""



# ─── public API ─────────────────────────────────────────────────────────────

async def generate_recommendations(
    profile: dict,
    reasoning_result: dict,
    ranked_docs: list[dict],
    user_query: str,
    llm_provider=None,
) -> tuple[list[RecommendationItem], str, bool]:
    """
    Generate structured recommendations.
    
    Returns:
        (recommendations, summary_message, is_demo_mode)
    """
    # Try LLM if available
    if llm_provider:
        try:
            available = await llm_provider.is_available()
            if available:
                logger.info("LLM provider: Ollama")
                logger.info(f"Model: {llm_provider.model}")
                logger.info(f"Retrieved evidence: {len(ranked_docs)}")
                
                system = SYSTEM_PROMPT
                user = _build_user_prompt(profile, reasoning_result, ranked_docs, user_query)
                raw_response, is_real = await llm_provider.generate(system, user)

                if is_real and raw_response:
                    recs, summary = _parse_llm_response(raw_response, ranked_docs)
                    if recs:
                        return recs, summary, False  # not demo mode
        except Exception as e:
            logger.warning(f"LLM generation failed, falling back: {e}")

    # Fallback: deterministic reasoning
    recs = generate_fallback_recommendations(reasoning_result, ranked_docs)
    summary = generate_summary_message(profile, reasoning_result, recs)
    return recs, summary, True


def _parse_llm_response(
    raw: str, ranked_docs: list[dict]
) -> tuple[list[RecommendationItem], str]:
    """
    Parse LLM JSON response into RecommendationItems.
    Validates that citations reference only retrieved evidence.
    """
    import re

    # Strip markdown code blocks if present
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON object
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except Exception:
                return [], ""
        else:
            return [], ""

    summary = data.get("summary_message", "")
    recs_raw = data.get("recommendations", [])

    # Build set of valid source titles from retrieved docs
    valid_sources = {
        doc.get("metadata", {}).get("title", "").lower()
        for doc in ranked_docs
    }

    recs = []
    for r in recs_raw:
        # Validate evidence items against retrieved docs
        evidence_items = []
        for ev in r.get("evidence", []):
            title = ev.get("title", "").lower()
            # Allow if it matches any retrieved doc (fuzzy)
            is_valid = any(
                title in vs or vs in title
                for vs in valid_sources
                if vs
            )
            if is_valid or not valid_sources:
                evidence_items.append(
                    EvidenceItem(
                        title=ev.get("title", ""),
                        source=ev.get("source", ""),
                        year=ev.get("year"),
                        url=ev.get("url"),
                        supporting_excerpt=ev.get("supporting_excerpt", ""),
                        topic=ev.get("topic"),
                        variables=ev.get("variables", []),
                    )
                )

        # If LLM evidence didn't validate, use retrieved docs directly
        if not evidence_items and ranked_docs:
            evidence_items = build_citations(ranked_docs[:2])

        if r.get("title") and r.get("action"):
            recs.append(
                RecommendationItem(
                    title=r["title"],
                    action=r["action"],
                    reasoning=r.get("reasoning", ""),
                    impacted_metrics=r.get("impacted_metrics", []),
                    time_horizon=r.get("time_horizon", "medium-term"),
                    confidence=r.get("confidence", "Medium"),
                    evidence=evidence_items,
                )
            )

    return recs, summary


def build_reasoning_trace(
    profile: dict,
    reasoning_result: dict,
    ranked_docs: list[dict],
    missing_vars: list[str],
) -> ReasoningTrace:
    """Build the reasoning trace for display in the UI."""
    active_vars = reasoning_result.get("active_variables", [])
    chain = reasoning_result.get("relationship_chain", [])

    variables_detected = format_active_variables_for_display(active_vars)

    evidence_titles = [
        doc.get("metadata", {}).get("title", "Evidence record")
        for doc in ranked_docs[:4]
    ]

    # Format missing_vars as readable strings
    missing_readable = []
    for q in missing_vars:
        # These are already questions — extract the variable name from them
        if "organic carbon" in q.lower():
            missing_readable.append("Soil organic carbon")
        elif "rainfall" in q.lower():
            missing_readable.append("Rainfall pattern")
        elif "cropping" in q.lower() or "crop" in q.lower():
            missing_readable.append("Cropping system")
        elif "region" in q.lower() or "location" in q.lower():
            missing_readable.append("Geographic region")
        elif "pH" in q or "ph" in q.lower():
            missing_readable.append("Soil pH")
        elif "pesticide" in q.lower():
            missing_readable.append("Pesticide pressure")
        else:
            missing_readable.append(q[:50])

    return ReasoningTrace(
        variables_detected=variables_detected,
        missing_variables=missing_readable,
        retrieved_evidence_count=len(ranked_docs),
        environmental_relationships=chain[:12],
        evidence_titles=evidence_titles,
    )
