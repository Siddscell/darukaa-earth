# RAG Pipeline

## Document Ingestion Flow
1. Source documents (PDFs, scientific papers, markdown) are processed.
2. Text is extracted and normalized.
3. Metadata is attached (source, year, confidence, environmental metrics).
4. Content is embedded and stored in ChromaDB.

## Chunking Strategy
We use semantic chunking, splitting documents into logical sections (paragraphs or sections) rather than arbitrary token lengths. This preserves the context of scientific claims. Chunk overlap is 10-20% to ensure context continuity.

## Embedding Model
We use `all-MiniLM-L6-v2` via `sentence-transformers`. It provides a good balance between performance (fast CPU inference) and semantic accuracy for scientific text.

## ChromaDB Collection Structure
Collections store:
- **ID**: Unique chunk ID
- **Embedding**: Vector representation
- **Document**: The text chunk
- **Metadata**: JSON containing source, tags, confidence level, and affected environmental metrics.

## Retrieval with Metadata Filtering
When a query is received, the user's environmental profile is used to generate metadata filters (e.g., filtering for "semi-arid" region or "soil_organic_carbon" metric). The query is embedded, and a vector search is performed on the filtered subset.

## Evidence Ranking Algorithm
Retrieved chunks are ranked based on:
1. Cosine similarity (vector distance)
2. Metadata match (does it match the user's specific context?)
3. Source confidence level (high confidence sources get boosted)

## Citation Grounding
The RAG pipeline builds explicit citations. The LLM prompt forces the model to use ONLY retrieved evidence and append citations like `[Source 1]` to its claims, preventing hallucinations.
