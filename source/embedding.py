from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding model"""
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Convert texts to embedding vectors"""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Convert query to embedding vector"""
        return self.embed_texts([query])[0]
