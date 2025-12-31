# Backend - Market Research Multi-Agent System

FastAPI backend with Azure AI Foundry SDK integration for multi-agent market research assistant.

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# Edit .env with your Azure credentials

# Run the server
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── core/            # Config, security, logging
│   ├── api/             # API routes
│   ├── rag/             # RAG pipeline
│   ├── kag/             # Knowledge graph
│   ├── storage/         # Azure Blob + DB
│   ├── services/        # Business logic
│   └── schemas/         # Pydantic models
└── requirements.txt
```
