from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from backend.database import SessionLocal
from rag.embedding import generate_embedding

model=SentenceTransformer("all-MiniLM-L6-v2")

def search_similar_chunks(question:str,top_k:int=3):
    query_embedding = generate_embedding(question)

    db=SessionLocal()

    try:
        results=db.execute(
            text("""
                SELECT id,content,metadata,embedding <=> CAST(:embedding as vector) AS distance
                from incident_chunks
                ORDER BY distance
                LIMIT :top_k
            """),
            {
                "embedding":str(query_embedding),
                "top_k":top_k
            }
        ).fetchall()
        return results
    finally:
        db.close()

if __name__=="__main__":
    question="Why is my VPN not connecting?"

    results=search_similar_chunks(question)

    for result in results:
        print("Content: ",result.content)
        print("Metadata: ",result.metadata)
        print("Distance: ",result.distance)
        print("--------------------")