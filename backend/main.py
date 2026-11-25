
from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db, Incident as IncidentDB,ChatMessage
from rag.pipeline import run_rag_pipeline


app = FastAPI(
    title="Enterprise AI Incident Intelligence Platform",
    description="AI-powered IT incident prediction and intelligence",
    version="1.0.0"
)


# Load ML model once when application starts
MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "ml"
    / "incident_priority_model.pkl"
)

model = joblib.load(MODEL_PATH)


class IncidentRequest(BaseModel):
    category: str
    subcategory: str
    contact_type: str
    u_symptom: str
    location: str
    opened_hour: int = Field(ge=0, le=23)

class ChatRequest(BaseModel):
    question:str=Field(min_length=1)
    session_id:str

def get_chat_history(session_id:str,db:Session):
    history=(
        db.query(ChatMessage)
        .filter(ChatMessage.session_id==session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return history


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Incident Intelligence API is running"
    }

@app.post("/chat")
def chat(request:ChatRequest,db:Session=Depends(get_db)):
    try:

        # Retriving the previous conversations of the session_id
        history=get_chat_history(request.session_id,db)

        # Saves the current user question
        user_message=ChatMessage(
            session_id=request.session_id,
            role="user",
            message=request.question
        )

        db.add(user_message)
        db.commit()

        #Generate answer using conversation history
        answer=run_rag_pipeline(request.question,history)

        # saves assistant response
        assist_message=ChatMessage(
            session_id=request.session_id,
            role="assistant",
            message=answer
        )

        db.add(assist_message)
        db.commit()

        return {
            "session_id": request.session_id,
            "question":request.question,
            "answer":answer
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate the answer"
        )


# Prediction endpoint
@app.post("/predict")
def predict_priority(
    incident: IncidentRequest,
    db: Session = Depends(get_db)
):

    try:
        incident_data = pd.DataFrame([
            incident.model_dump()
        ])

        prediction = model.predict(incident_data)[0]

        db_incident = IncidentDB(
            category=incident.category,
            subcategory=incident.subcategory,
            contact_type=incident.contact_type,
            u_symptom=incident.u_symptom,
            location=incident.location,
            opened_hour=incident.opened_hour,
            predicted_priority=str(prediction)
        )

        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)

        return {
            "incident_id": db_incident.id,
            "predicted_priority": str(prediction),
            "message": "Incident predicted and saved successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Prediction or database operation failed"
        )


@app.get("/chat/history/{session_id}")
def chat_history(
    session_id:str,
    db:Session=Depends(get_db)
):
    history=get_chat_history(session_id,db)

    return [
        {
            "role":message.role,
            "message":message.message
        }
        for message in history
    ]
