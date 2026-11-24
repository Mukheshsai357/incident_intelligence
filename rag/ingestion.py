from rag.embedding import generate_embedding
from sqlalchemy.orm import Session
from pathlib import Path
from sqlalchemy import text

from backend.database import SessionLocal,IncidentChunk


KNOWLEDGE_BASE=Path("data/knowledge_base")

def split_into_chunks(text,chunk_size=180,overlap=30):
    words=text.split()

    chunks=[]
    start=0
    while start<len(words):
        end=start+chunk_size

        chunk=" ".join(words[start:end])
        chunks.append(chunk)

        start+=chunk_size-overlap
    return chunks

def ingest_documents():
    db=SessionLocal()
    try:
        for file_path in KNOWLEDGE_BASE.glob("*.md"):
            print(f"Processing: {file_path.name}")

            # Remove previously stored chunks from this document

            db.execute(
                text("""
                    DELETE from incident_chunks
                    where metadata ->> 'source'=CAST(:source AS TEXT)
                """).bindparams(source=file_path.name)
            ) 

            content=file_path.read_text(encoding="utf-8")
            chunks=split_into_chunks(content)

            for index,chunk_text in enumerate(chunks):
                embedding = generate_embedding(chunk_text)

                chunk=IncidentChunk(
                    content=chunk_text,
                    embedding=embedding,
                    chunk_metadata={
                        "source":file_path.name,
                        "chunk_index":index
                    }
                )

                db.add(chunk)
        db.commit()
        print("All documents ingested successfully!")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()  


def store_chunk(content:str,metadata:dict):
    embedding = generate_embedding(content)

    db=SessionLocal()

    try:
        chunk=IncidentChunk(
            content=content,
            embedding=embedding,
            chunk_metadata=metadata
        )
        db.add(chunk)
        db.commit()

        print("Chunk created successfully!")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



if __name__ == "__main__":
    ingest_documents()
