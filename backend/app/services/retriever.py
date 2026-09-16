"""
Retriever: semantic + metadata-filtered document retrieval from ChromaDB.
"""
import logging
from typing import Optional
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.config import settings

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self):
        self.embedding_svc = EmbeddingService()
        self.vector_store = VectorStoreService()

    def retrieve(
        self,
        query: str,
        env_profile: Optional[dict] = None,
        topic_filter: Optional[str] = None,
        n_results: int = None,
        active_variables: Optional[list[str]] = None,
    ) -> list[dict]:
        """
        Retrieve relevant documents for a query.
        Applies optional metadata filter by topic.
        Returns list of dicts with keys: id, document, metadata, distance.
        """
        n = n_results or settings.MAX_RETRIEVED_DOCS

        try:
            # Embed the query
            embedding = self.embedding_svc.embed_texts([query])
            query_embedding = embedding[0].tolist()

            # Build where filter
            where = None
            if topic_filter:
                where = {"topic": {"$eq": topic_filter}}

            # Search ChromaDB
            results = self.vector_store.search(
                query_embeddings=[query_embedding],
                n_results=n,
                where=where,
            )

            # Normalize ChromaDB results into flat dicts
            docs = self._normalize_results(results)
            return docs

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []

    def retrieve_multi_topic(
        self,
        query: str,
        topics: list[str],
        n_per_topic: int = 2,
    ) -> list[dict]:
        """
        Retrieve documents across multiple topics and combine results.
        Useful for multi-metric reasoning queries.
        """
        all_docs = []
        seen_ids = set()

        for topic in topics:
            docs = self.retrieve(query, topic_filter=topic, n_results=n_per_topic)
            for doc in docs:
                doc_id = doc.get("id", "")
                if doc_id not in seen_ids:
                    all_docs.append(doc)
                    seen_ids.add(doc_id)

        return all_docs

    def _normalize_results(self, chroma_results: dict) -> list[dict]:
        """Convert ChromaDB query results to a flat list of dicts."""
        if not chroma_results:
            return []

        ids = chroma_results.get("ids", [[]])[0]
        documents = chroma_results.get("documents", [[]])[0]
        metadatas = chroma_results.get("metadatas", [[]])[0]
        distances = chroma_results.get("distances", [[]])[0]

        result = []
        for i, doc_id in enumerate(ids):
            meta = metadatas[i] if i < len(metadatas) else {}
            # Parse JSON strings in metadata
            if isinstance(meta.get("variables"), str):
                try:
                    import json
                    meta["variables"] = json.loads(meta["variables"])
                except Exception:
                    meta["variables"] = []

            result.append({
                "id": doc_id,
                "text": documents[i] if i < len(documents) else "",
                "document": documents[i] if i < len(documents) else "",
                "metadata": meta,
                "distance": distances[i] if i < len(distances) else 1.0,
            })

        return result
