import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any
import hashlib

class ChromaDBManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )

    def get_or_create_collection(self, name: str = "notes"):
        """Get or create a collection"""
        try:
            collection = self.client.get_collection(name=name)
        except:
            collection = self.client.create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        return collection

    def _prepare_metadatas(self, metadatas: List[Dict]) -> List[Dict]:
        """Convert any unsupported metadata types to strings."""
        prepared_metadatas = []
        for metadata_item in metadatas:
            prepared_item = {}
            for key, value in metadata_item.items():
                if isinstance(value, (type(None), str, int, float, bool)):
                    prepared_item[key] = value
                else:
                    prepared_item[key] = str(value)
            prepared_metadatas.append(prepared_item)
        return prepared_metadatas

    def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to the collection"""
        collection = self.get_or_create_collection()
        prepared_metadatas = self._prepare_metadatas(metadatas)

        collection.add(
            documents=documents,
            metadatas=prepared_metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 5):
        """Query similar documents"""
        collection = self.get_or_create_collection()
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

    def reset(self):
        """Reset the database"""
        self.client.reset()

    def get_stats(self):
        """Get database statistics"""
        collection = self.get_or_create_collection()
        return collection.count()
