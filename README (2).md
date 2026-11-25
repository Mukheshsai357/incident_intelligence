# Enterprise AI Incident Intelligence Platform

An AI-powered IT incident intelligence application combining machine-learning-based incident priority prediction with a retrieval-augmented generation (RAG) chatbot for IT troubleshooting.

## Features

- Predict incident priority from incident details available at creation time.
- Store incident details and predictions in PostgreSQL.
- Ingest Markdown troubleshooting documents, split them into overlapping chunks, generate embeddings, and store them using pgvector.
- Retrieve relevant knowledge chunks using vector similarity search.
- Generate context-grounded IT support answers using a Groq-hosted LLM.
- Store user and assistant messages by session ID. Retrieving and using prior messages as conversational context is still in development.

## Technology Stack

- Python 3.12
- FastAPI and Uvicorn
- Scikit-learn, pandas, NumPy, and Joblib
- PostgreSQL and pgvector
- SQLAlchemy
- Sentence Transformers (`all-MiniLM-L6-v2`, 384-dimensional embeddings)
- Groq API (`openai/gpt-oss-20b`)
- Git and GitHub

## Project Structure

```text
enterprise-ai-incident-platform/
├── agents/                         # Agent workflows (planned/in development)
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application and endpoints
│   └── database.py                 # SQLAlchemy models and DB connection
├── data/
│   └── knowledge_base/             # Markdown IT troubleshooting documents
├── frontend/                       # Frontend application (planned)
├── ml/
│   └── incident_priority_model.pkl # Trained priority prediction model
├── notebooks/                      # EDA and model experiments
├── rag/
│   ├── embedding.py                 # Shared embedding model/function
│   ├── ingestion.py                 # Knowledge-base ingestion
│   ├── retrieval.py                 # pgvector similarity search
│   ├── generation.py                # Groq-based answer generation
│   └── pipeline.py                  # End-to-end RAG pipeline
├── tests/                           # Automated tests (to be added)
├── .env                             # Local secrets (do not commit)
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

Install separately:
1. Python 3.12
2. PostgreSQL (developed with PostgreSQL 18)
3. The pgvector extension compatible with your PostgreSQL installation
4. Git

A Groq API key is required for LLM answer generation.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mukheshsai357/incident_intelligence.git
cd incident_intelligence
```

### 2. Create and activate a virtual environment

Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate
```

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/incident_intelligence
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Replace the placeholders with your local PostgreSQL password and Groq API key. Never commit `.env` or share its contents.

If `backend/database.py` currently constructs the database URL directly rather than reading `DATABASE_URL`, update it to read this environment variable or adjust the example to match your implementation.

### 5. Create the database and enable pgvector

Create a database named `incident_intelligence`, connect to it, and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The pgvector extension must first be installed on the PostgreSQL server.

### 6. Add the trained ML model

The API expects this file:

```text
ml/incident_priority_model.pkl
```

If it is absent after cloning, place your locally trained model at that path or train/export the model again. Do not load model files from untrusted sources.

### 7. Add knowledge-base documents

Place your Markdown troubleshooting documents (`.md`) inside:

```text
data/knowledge_base/
```

### 8. Ingest the knowledge base

Run from the repository root:

```bash
python -m rag.ingestion
```

Run ingestion again after updating source documents, following the replacement behavior implemented in the ingestion script.

## Run the API

With the virtual environment activated, run from the repository root:

```bash
uvicorn backend.main:app --reload
```

Open Swagger documentation at:

`http://127.0.0.1:8000/docs`

## Main API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Check that the API is running |
| `POST` | `/predict` | Predict incident priority and save the incident |
| `POST` | `/chat` | Ask the RAG-based IT support chatbot |

### Example chat request

```json
{
  "session_id": "user_session_001",
  "question": "Why is my VPN not connecting?"
}
```

The current chat endpoint stores user and assistant messages using the supplied session ID. Check `/docs` for the current request schema if it changes.

## Notes and Limitations

- The priority model is a prototype. The dataset is imbalanced, and minority-class performance needs improvement before operational use.
- The RAG similarity-distance threshold is experimental and should be evaluated on a representative test set.
- The chatbot can answer only when the ingested knowledge base provides relevant context; it should say when the context is insufficient.
- Persisting chat messages does not automatically mean previous messages are retrieved and used as conversational context.
- Authentication, session ownership, automated tests, frontend, containerization, deployment, and monitoring are planned or still in development.

## Security

- Keep `.env`, API keys, passwords, virtual environments, and local caches out of version control.
- Do not commit private or sensitive incident data.
- Only load trusted model artifacts.

## License

Add a license before distributing or reusing this project publicly.
