from functools import lru_cache
from sentence_transformers import SentenceTransformer

EMBEDDING_DIMENSION = 384

@lru_cache(maxsize=1)
def encoder():
    return SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def embed_text(text, dimension=EMBEDDING_DIMENSION):
    if dimension != EMBEDDING_DIMENSION:
        raise ValueError("Expected 384 dimensions")
    return encoder().encode(text, normalize_embeddings=True).tolist()
