"""
Citation builder: converts raw ChromaDB results into EvidenceItem schema objects.
Only builds citations from actually retrieved documents.
"""
from typing import Optional
from app.schemas.chat import EvidenceItem


def _safe_int(val) -> Optional[int]:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _safe_list(val) -> list:
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        try:
            import json
            parsed = json.loads(val)
            return parsed if isinstance(parsed, list) else []
        except Exception:
            return []
    return []


def build_citations(docs: list[dict], max_per_rec: int = 2) -> list[EvidenceItem]:
    """
    Convert a list of retrieved (and ranked) documents into EvidenceItem objects.
    
    IMPORTANT: Only documents that were actually retrieved are used.
    Never fabricates or invents citations.
    
    Returns up to max_per_rec EvidenceItems.
    """
    if not docs:
        return []

    items = []
    for doc in docs[:max_per_rec]:
        meta = doc.get("metadata", {})
        text = doc.get("text", doc.get("document", ""))

        # Extract a relevant supporting excerpt (first 400 chars)
        excerpt = text.strip()
        if len(excerpt) > 400:
            # Try to end at a sentence boundary
            truncated = excerpt[:400]
            last_period = truncated.rfind(".")
            if last_period > 200:
                excerpt = truncated[: last_period + 1]
            else:
                excerpt = truncated + "..."

        item = EvidenceItem(
            title=meta.get("title") or "Environmental Evidence Record",
            source=meta.get("source") or "Unknown Source",
            year=_safe_int(meta.get("year")),
            url=meta.get("url") or None,
            supporting_excerpt=excerpt or "No text available.",
            topic=meta.get("topic") or "general",
            variables=_safe_list(meta.get("variables")),
        )
        items.append(item)

    return items


def build_all_citations(docs: list[dict]) -> list[EvidenceItem]:
    """Build EvidenceItems from all retrieved docs (used for evidence library)."""
    return [build_citations([doc], max_per_rec=1)[0] for doc in docs if doc]
