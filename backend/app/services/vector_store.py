import chromadb
from app.config import settings

class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(name=settings.CHROMA_COLLECTION_EVIDENCE)
        
    def add_documents(self, ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]]):
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
        
    def search(self, query_embeddings: list[list[float]], n_results: int = 5, where: dict = None):
        return self.collection.query(query_embeddings=query_embeddings, n_results=n_results, where=where)
        
    def get_collection_count(self) -> int:
        return self.collection.count()
        
    def collection_exists(self) -> bool:
        return True
