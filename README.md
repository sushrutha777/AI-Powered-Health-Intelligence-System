# 🏥 AI-Powered Health Intelligence System

A production-grade, full-stack healthcare platform powered by AI — providing disease prediction, heart disease risk assessment, drug recommendations, and a RAG-based medical chatbot.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16+-000000?logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-2.18+-0194E2?logo=mlflow&logoColor=white)

---

## ✨ Features

| Feature | Model / Tech | Endpoint |
|---------|-------------|----------|
| **Disease Prediction** | RandomForest (scikit-learn) | `POST /api/v1/disease/predict` |
| **Heart Risk Assessment** | LightGBM | `POST /api/v1/heart/assess` |
| **Drug Recommendations** | TF-IDF + Cosine Similarity | `POST /api/v1/drug/recommend` |
| **Medical AI Chatbot** | RAG (FAISS + LLM) | `POST /api/v1/chat/message` |
| **User Authentication** | JWT + bcrypt | `POST /api/v1/auth/login` |

---

## 🏗️ Architecture

```
Frontend (Next.js)  →  Backend (FastAPI)  →  PostgreSQL
                           ↓
                    ML Services Layer
                    ├── RandomForest (Disease)
                    ├── LightGBM (Heart)
                    ├── TF-IDF (Drug Rec)
                    └── FAISS + LLM (RAG Chatbot)
                           ↓
                    MLflow Model Registry
```

---

## 📁 Project Structure

```
├── backend/
│   ├── src/
│   │   ├── api/v1/endpoints/    # Route handlers
│   │   ├── core/                # Config, security, logging
│   │   ├── db/                  # Database engine & session
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic validation schemas
│   │   └── services/            # Business logic + RAG pipeline
│   ├── ml/                      # Training pipelines & model artifacts
│   ├── tests/                   # Pytest async tests
│   ├── alembic/                 # Database migrations
│   └── pyproject.toml           # Python dependencies
├── frontend/
│   ├── src/app/                 # Next.js App Router pages
│   ├── src/lib/                 # API client, auth context
│   └── src/types/               # TypeScript type definitions
├── docker-compose.yml           # PostgreSQL + Backend + MLflow
└── .github/workflows/ci.yml     # GitHub Actions CI pipeline
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Access:
# Frontend  → http://localhost:3000
# Backend   → http://localhost:8000
# API Docs  → http://localhost:8000/docs
# MLflow    → http://localhost:5000
```

### Option 2: Manual Setup

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -e ".[dev]"
cp .env.example .env           # Edit with your DB credentials
alembic upgrade head           # Run migrations
uvicorn src.main:app --reload  # Start backend at :8000

# Frontend
cd frontend
npm install
npm run dev                    # Start frontend at :3000
```

---

## 🔐 Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async connection string |
| `JWT_SECRET_KEY` | Secret key for JWT signing |
| `HUGGINGFACE_API_KEY` | HuggingFace API key for RAG chatbot |
| `MLFLOW_TRACKING_URI` | MLflow tracking server URL |

---

## 🧪 Running Tests

```bash
cd backend
pytest -v --cov=src
```

---

## 📊 ML Model Training

```bash
cd backend

# Train disease prediction model
python -m ml.training.disease_trainer

# Train heart disease model
python -m ml.training.heart_trainer

# Build FAISS vector index for RAG
python -m ml.scripts.build_vector_index
```

---

## 🛠️ Tech Stack

- **Frontend:** Next.js 16, TypeScript, CSS
- **Backend:** FastAPI, SQLAlchemy (async), Pydantic v2
- **Database:** PostgreSQL 16
- **Auth:** JWT (python-jose) + bcrypt
- **ML:** scikit-learn, LightGBM, sentence-transformers, FAISS
- **LLM:** HuggingFace Inference API
- **MLOps:** MLflow, Docker
- **CI/CD:** GitHub Actions

---

## 📄 License

This project is for educational and portfolio purposes.
