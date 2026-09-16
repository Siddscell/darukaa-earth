import json
import pytest
from unittest.mock import AsyncMock
from app.llm.provider import LLMProvider
from app.reasoning.recommendation_engine import (
    generate_recommendations,
    _parse_llm_response,
    _build_user_prompt,
    SYSTEM_PROMPT,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FULL_PROFILE = {
    "region": "Maharashtra",
    "soil": {"organic_carbon_percent": 0.3},
    "land_use": {"primary_type": "cropland", "crop": "wheat"},
    "biodiversity": {"species_richness": "low", "habitat_diversity": "low"},
    "climate": {"rainfall_pattern": "low"},
}

FULL_REASONING = {
    "active_variables": ["soil_organic_carbon", "rainfall", "biodiversity_decline"],
    "relationship_chain": [
        "Soil Organic Carbon \u2192 water retention",
        "Rainfall \u2192 vegetation survival",
        "Biodiversity Decline \u2192 habitat quality",
    ],
    "interventions": ["cover_crops", "water_harvesting", "reduced_tillage"],
    "intervention_details": [
        {
            "title": "Cover Crops",
            "action": "Plant leguminous cover crops",
            "reasoning": "Helps build SOC",
            "impacted_metrics": ["soil_organic_carbon"],
            "time_horizon": "medium-term",
            "confidence": "High",
        }
    ],
}

REAL_DOCS = [
    {
        "metadata": {
            "title": "Soil Organic Carbon and Agricultural Productivity",
            "source": "CGIAR",
            "year": 2021,
            "url": "https://cgiar.org/",
            "topic": "soil",
            "variables": ["soil_organic_carbon", "water_retention"],
        },
        "text": "Low SOC is a primary driver of reduced water retention in dryland systems.",
    },
    {
        "metadata": {
            "title": "Climate Change and Dryland Agriculture: IPCC Findings",
            "source": "IPCC",
            "year": 2021,
            "url": "https://ipcc.ch/",
            "topic": "climate",
            "variables": ["rainfall", "crop_production"],
        },
        "text": "Semi-arid regions face compounding stress from low rainfall and degraded soils.",
    },
]

_VALID_LLM_RESPONSE = json.dumps({
    "summary_message": "Your wheat farm in Maharashtra faces low SOC and rainfall stress. Here are targeted interventions.",
    "recommendations": [
        {
            "title": "Introduce Drought-Tolerant Legume Intercrop",
            "action": "During the kharif season, sow drought-tolerant pigeonpea or cowpea between wheat rows.",
            "reasoning": (
                "With SOC at 0.3% and low rainfall, your soil has reduced water retention capacity. "
                "Legume intercrops fix atmospheric nitrogen, add organic matter, and improve soil structure, "
                "addressing both low SOC and moisture stress. Species diversification also partially mitigates "
                "biodiversity decline by introducing non-wheat plant cover."
            ),
            "impacted_metrics": ["soil_organic_carbon", "water_retention", "species_richness"],
            "time_horizon": "medium-term",
            "confidence": "High",
            "evidence": [
                {
                    "title": "Soil Organic Carbon and Agricultural Productivity",
                    "source": "CGIAR",
                    "year": 2021,
                    "url": "https://cgiar.org/",
                    "supporting_excerpt": "Low SOC is a primary driver of reduced water retention in dryland systems.",
                    "topic": "soil",
                    "variables": ["soil_organic_carbon", "water_retention"],
                }
            ],
        }
    ],
})


@pytest.fixture
def mock_llm_provider():
    provider = LLMProvider()
    provider._ollama.is_available = AsyncMock(return_value=True)
    provider._ollama.generate = AsyncMock(return_value=_VALID_LLM_RESPONSE)
    return provider


@pytest.fixture
def unavailable_llm_provider():
    provider = LLMProvider()
    provider._ollama.is_available = AsyncMock(return_value=False)
    return provider


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ---------------------------------------------------------------------------
# Prompt content tests (no server required)
# ---------------------------------------------------------------------------

def test_prompt_contains_environmental_profile():
    """LLM receives the full environmental profile."""
    prompt = _build_user_prompt(FULL_PROFILE, FULL_REASONING, REAL_DOCS, "test query")
    assert "Maharashtra" in prompt
    assert "0.3" in prompt
    assert "wheat" in prompt
    assert "low" in prompt


def test_prompt_contains_retrieved_evidence():
    """LLM receives retrieved evidence titles and text."""
    prompt = _build_user_prompt(FULL_PROFILE, FULL_REASONING, REAL_DOCS, "test query")
    assert "Soil Organic Carbon and Agricultural Productivity" in prompt
    assert "Climate Change and Dryland Agriculture" in prompt
    # Text excerpts should also be present
    assert "water retention" in prompt


def test_prompt_contains_reasoning_context():
    """LLM receives active stressors and relationship chain."""
    prompt = _build_user_prompt(FULL_PROFILE, FULL_REASONING, REAL_DOCS, "test query")
    assert "soil_organic_carbon" in prompt.lower() or "0.3%" in prompt
    assert "cover_crops" in prompt


def test_system_prompt_includes_no_hallucination_rules():
    """System prompt instructs model not to invent numbers or citations."""
    assert "Do NOT invent" in SYSTEM_PROMPT
    assert "invent" in SYSTEM_PROMPT.lower()
    assert "exact title" in SYSTEM_PROMPT.lower()


def test_system_prompt_requires_multi_stressor_reasoning():
    """System prompt requires connecting at least two stressors."""
    assert "two" in SYSTEM_PROMPT.lower() or "multi" in SYSTEM_PROMPT.lower()


# ---------------------------------------------------------------------------
# Structured output tests
# ---------------------------------------------------------------------------

def test_structured_output_parsing():
    """Valid JSON LLM response parses correctly into RecommendationItem."""
    recs, summary = _parse_llm_response(_VALID_LLM_RESPONSE, REAL_DOCS)
    assert summary != ""
    assert len(recs) == 1
    assert recs[0].title == "Introduce Drought-Tolerant Legume Intercrop"
    assert recs[0].time_horizon == "medium-term"
    assert recs[0].confidence == "High"
    assert "soil_organic_carbon" in recs[0].impacted_metrics


def test_malformed_json_returns_empty():
    """Completely invalid JSON returns empty results rather than crashing."""
    recs, summary = _parse_llm_response("this is not json at all", [])
    assert recs == []
    assert summary == ""


# ---------------------------------------------------------------------------
# Citation validation tests
# ---------------------------------------------------------------------------

def test_unsupported_citations_are_rejected():
    """Citations not in retrieved docs are stripped and replaced."""
    raw = json.dumps({
        "summary_message": "Msg",
        "recommendations": [{
            "title": "Real Rec",
            "action": "Do something",
            "evidence": [{"title": "Completely Fabricated Study 2099"}],
        }],
    })
    docs = [{"metadata": {"title": "Real Document", "source": "Real Source", "topic": "soil"}}]
    recs, _ = _parse_llm_response(raw, docs)
    assert len(recs) == 1
    # Fabricated title should be replaced with real retrieved doc
    assert recs[0].evidence[0].title == "Real Document"


def test_valid_citations_are_kept():
    """Citations matching retrieved docs pass through correctly."""
    raw = json.dumps({
        "summary_message": "Summary",
        "recommendations": [{
            "title": "Good Rec",
            "action": "Do something",
            "evidence": [{
                "title": "Real Document",
                "source": "Real Source",
                "year": 2020,
                "supporting_excerpt": "Some excerpt",
                "topic": "soil",
                "variables": ["water_retention"],
            }],
        }],
    })
    docs = [{"metadata": {"title": "Real Document", "source": "Real Source", "topic": "soil"}}]
    recs, _ = _parse_llm_response(raw, docs)
    assert len(recs) == 1
    assert recs[0].evidence[0].title == "Real Document"
    assert recs[0].evidence[0].source == "Real Source"


def test_hallucinated_numerical_claims_not_in_schema():
    """
    Parser does not add or enforce hallucinated numbers — it only
    validates citation grounding. Confirms schema is structural only.
    """
    raw = json.dumps({
        "summary_message": "Hallucinated numbers present",
        "recommendations": [{
            "title": "Rec with numbers",
            "action": "Do X and increase yields by 500%",
            "reasoning": "SOC increases by 15% per year (fabricated)",
            "impacted_metrics": ["soil_organic_carbon"],
            "time_horizon": "short-term",
            "confidence": "High",
            "evidence": [{"title": "Soil Organic Carbon and Agricultural Productivity"}],
        }],
    })
    # The citation title matches the retrieved doc, so it passes
    recs, _ = _parse_llm_response(raw, REAL_DOCS)
    assert len(recs) == 1
    # The parser does not strip numbers from free text — that is the system prompt's job
    # What matters is the citation is grounded
    assert recs[0].evidence[0].title == "Soil Organic Carbon and Agricultural Productivity"


# ---------------------------------------------------------------------------
# Async integration tests (mocked Ollama — no live server required)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_ollama_unavailable_fallback(unavailable_llm_provider):
    """If Ollama is unavailable, fallback is used and demo_mode is True."""
    recs, summary, is_demo = await generate_recommendations(
        profile={},
        reasoning_result={
            "active_variables": ["soil_organic_carbon"],
            "relationship_chain": [],
            "intervention_details": [{
                "title": "Cover Crops",
                "action": "Plant them",
                "reasoning": "Helps soil",
                "impacted_metrics": ["soil"],
                "time_horizon": "short-term",
                "confidence": "High",
            }],
        },
        ranked_docs=[],
        user_query="test",
        llm_provider=unavailable_llm_provider,
    )
    assert is_demo is True
    assert len(recs) > 0


@pytest.mark.anyio
async def test_ollama_available_selected(mock_llm_provider):
    """If Ollama is available, provider is used and demo_mode is False."""
    recs, summary, is_demo = await generate_recommendations(
        profile=FULL_PROFILE,
        reasoning_result=FULL_REASONING,
        ranked_docs=REAL_DOCS,
        user_query="What should I do with my wheat farm?",
        llm_provider=mock_llm_provider,
    )
    assert is_demo is False
    assert len(recs) == 1
    assert "Legume Intercrop" in recs[0].title or recs[0].title != ""


@pytest.mark.anyio
async def test_ollama_parse_failure_falls_back(unavailable_llm_provider):
    """If LLM returns garbage, fallback is used."""
    broken_provider = LLMProvider()
    broken_provider._ollama.is_available = AsyncMock(return_value=True)
    broken_provider._ollama.generate = AsyncMock(return_value="NOT JSON AT ALL {{{{")

    recs, summary, is_demo = await generate_recommendations(
        profile=FULL_PROFILE,
        reasoning_result=FULL_REASONING,
        ranked_docs=REAL_DOCS,
        user_query="test",
        llm_provider=broken_provider,
    )
    # Falls back to deterministic — still produces recs, demo_mode True
    assert is_demo is True
    assert len(recs) > 0
