cat > README.md << 'EOF'
# Finance Intelligence Agent

AI-powered personal finance manager with natural language queries,
expense categorisation, spending prediction, and anomaly detection.

## Tech Stack
- **Frontend:** React + TypeScript + Tailwind CSS
- **Backend:** FastAPI + PostgreSQL + Redis
- **AI/ML:** LangChain + OpenAI + scikit-learn
- **Infra:** Docker + Celery + GitHub Actions

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.11+
- Node.js 20+

### Run Locally

1. Clone the repo
   git clone https://github.com/YOUR_USERNAME/finance-intelligence-agent.git
   cd finance-intelligence-agent

2. Setup environment
   cp .env.example .env
   # .env mein apni API keys daalo

3. Start infrastructure
   docker compose up -d

4. Start backend (Day 3 ke baad)
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload

5. Start frontend (Day 6 ke baad)
   cd frontend
   npm install
   npm run dev

## Project Structure
   frontend/    React SPA
   backend/     FastAPI + ML services
   ml/          Model training notebooks
   docker/      Dockerfiles

## Day-wise Progress
- [x] Day 1: Project setup & environment
- [ ] Day 2: PostgreSQL schema design
- [ ] Day 3: FastAPI project structure
   ...
EOF