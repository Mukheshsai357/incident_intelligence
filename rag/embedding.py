from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    model=get_embedding_model()
    return model.encode(text).tolist()