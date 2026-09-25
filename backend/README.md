# Backend - AI RAG Assistant

## Run locally

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
# On macOS/Linux use: cp .env.example .env
```

Put your Gemini API key in `.env` as `GEMINI_API_KEY=...`.

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs
