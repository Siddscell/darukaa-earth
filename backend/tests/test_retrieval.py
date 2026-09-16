import pytest

from app.rag.pipeline import RAGPipeline
from app.services.vector_store import VectorStoreService


@pytest.fixture
def rag_pipeline():
    return RAGPipeline()


@pytest.fixture
def vector_store():
    return VectorStoreService()


def test_retrieval_soil_organic_carbon(rag_pipeline, vector_store):
    if vector_store.get_collection_count() == 0:
        pytest.skip("ChromaDB is empty. Run ingestion first.")

    result = rag_pipeline.run(
        query="low soil organic carbon and water retention",
        env_profile={"soil": {"organic_carbon_percent": 0.3}},
    )

    ranked_docs = result.get("ranked_docs", [])

    assert len(ranked_docs) > 0

    topics = [
        doc.get("metadata", {}).get("topic", "").lower()
        for doc in ranked_docs
    ]
    texts = [
        doc.get("text", "").lower()
        for doc in ranked_docs
    ]

    assert (
        "soil" in topics
        or any("organic carbon" in text or "water retention" in text for text in texts)
    )


def test_retrieval_wheat_monoculture(rag_pipeline, vector_store):
    if vector_store.get_collection_count() == 0:
        pytest.skip("ChromaDB is empty. Run ingestion first.")

    result = rag_pipeline.run(
        query="wheat monoculture biodiversity habitat",
        env_profile={
            "land_use": {
                "cropping_system": "monoculture",
                "crop": "wheat",
            }
        },
    )

    ranked_docs = result.get("ranked_docs", [])

    assert len(ranked_docs) > 0

    topics = [
        doc.get("metadata", {}).get("topic", "").lower()
        for doc in ranked_docs
    ]
    texts = [
        doc.get("text", "").lower()
        for doc in ranked_docs
    ]

    assert (
        "biodiversity" in topics
        or "land_use" in topics
        or any("biodiversity" in text or "monoculture" in text for text in texts)
    )


def test_retrieval_low_rainfall(rag_pipeline, vector_store):
    if vector_store.get_collection_count() == 0:
        pytest.skip("ChromaDB is empty. Run ingestion first.")

    result = rag_pipeline.run(
        query="low rainfall agroforestry biodiversity",
        env_profile={"climate": {"rainfall_pattern": "low"}},
    )

    ranked_docs = result.get("ranked_docs", [])

    assert len(ranked_docs) > 0

    texts = [
        doc.get("text", "").lower()
        for doc in ranked_docs
    ]

    assert any(
        keyword in text
        for text in texts
        for keyword in ["agroforestry", "rainfall", "water", "biodiversity"]
    )
