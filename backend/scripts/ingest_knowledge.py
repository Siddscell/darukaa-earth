import os
import json
import sys

# Add backend directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStoreService
from app.services.document_chunker import chunk_text
from app.services.document_loader import load_json_records

def ingest_seed_data():
    print("Initializing services...")
    embedding_svc = EmbeddingService()
    # It's an async method but we can call the synchronous part or run async
    # Let's import asyncio
    import asyncio
    
    async def run_ingestion():
        await embedding_svc.initialize()
        vector_store = VectorStoreService()
        
        filepath = os.path.join(os.path.dirname(__file__), '..', 'data', 'seed', 'evidence_records.json')
        print(f"Loading documents from {filepath}...")
        records = load_json_records(filepath)
        
        ids = []
        documents = []
        metadatas = []
        
        for record in records:
            # We'll use the record text as the main document. 
            # In a real app we might chunk it, but these are small seed records.
            text = record.get('text', '')
            
            ids.append(record['id'])
            documents.append(text)
            
            # Prepare metadata (Chroma requires str, int, float, bool)
            meta = {
                "title": record.get('title', ''),
                "source": record.get('source', ''),
                "year": record.get('year', 0),
                "topic": record.get('topic', ''),
                "region": record.get('region', ''),
                "evidence_type": record.get('evidence_type', ''),
                "url": record.get('url', ''),
                # Store variables as JSON string to comply with Chroma's metadata rules
                "variables": json.dumps(record.get('variables', []))
            }
            metadatas.append(meta)
            
        print(f"Embedding {len(documents)} documents...")
        embeddings = embedding_svc.embed_texts(documents).tolist()
        
        print(f"Inserting into ChromaDB...")
        vector_store.add_documents(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        print("Ingestion complete. Total documents in collection:", vector_store.get_collection_count())

    asyncio.run(run_ingestion())
    
if __name__ == '__main__':
    ingest_seed_data()
