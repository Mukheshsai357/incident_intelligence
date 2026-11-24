
import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    subcategory = Column(String)
    contact_type = Column(String)
    u_symptom = Column(String)
    location = Column(String)
    opened_hour = Column(Integer)
    predicted_priority = Column(String)


class IncidentChunk(Base):
    __tablename__="incident_chunks"

    id=Column(Integer,primary_key=True,index=True)
    content=Column(Text,nullable=False)
    embedding=Column(Vector(384))
    chunk_metadata = Column("metadata", JSONB)
    created_at=Column(DateTime,server_default=func.now())

class ChatMessage(Base):
    __tablename__="chat_messages"

    id=Column(Integer,primary_key=True,index=True)
    session_id=Column(String,index=True,nullable=False)
    role=Column(String,nullable=False)
    message=Column(Text,nullable=False)
    created_at=Column(DateTime,server_default=func.now())

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
