# AI RAG Assistant — Angular + FastAPI + Gemini

A portfolio-ready Retrieval Augmented Generation (RAG) chatbot with:

- Angular 22 standalone frontend
- FastAPI Python backend
- Gemini generation + embeddings
- Lightweight JSON + NumPy vector store
- PDF / Markdown / TXT ingestion
- Chunking + overlap
- Top-k cosine-similarity retrieval
- Grounded answers with retrieved-source cards
- CORS, environment variables, Docker and tests
- Free-friendly deployment using Netlify + Render

## 1. Architecture

```text
Browser (Angular)
      |
      | POST /api/chat
      | POST /api/documents/upload
      v
FastAPI Backend
      |
      +--> document parser
      +--> chunker
      +--> Gemini Embeddings
      +--> local vector store (NumPy)
      +--> top-k retrieval
      +--> Gemini Chat Model
      |
      v
JSON API --> Angular UI
```

## 2. RAG flow

### Ingestion
1. User uploads a PDF/MD/TXT file.
2. FastAPI extracts text.
3. Text is split into overlapping chunks.
4. Each chunk is converted to an embedding vector.
5. Vectors + source metadata are saved to `backend/data/vector_index.json`.

### Query
1. Angular sends the question and recent chat history.
2. FastAPI creates a query embedding.
3. NumPy performs cosine similarity against indexed vectors.
4. Top-k chunks are placed into a grounded prompt.
5. Gemini generates the response.
6. Backend returns the answer plus retrieved sources.
7. Angular renders both the answer and evidence cards.

## 3. Why this is stronger than an ordinary chatbot

A simple LLM wrapper proves that you can call an AI API. This project proves more: RAG architecture, embeddings, semantic retrieval, document processing, REST API design, frontend integration, deployment, and AI-specific error handling.

## 4. Local setup

### Prerequisites

- Node.js 20+
- Python 3.11+
- A Gemini API key

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
# macOS/Linux: cp .env.example .env
```

Set `GEMINI_API_KEY` in `.env`, then:

```bash
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
npm start
```

Open http://localhost:4200.

The demo starts with a built-in Angular AI notes document. You can upload your own portfolio/resume/project documents from the UI.

## 5. Test the API without Angular

Health:

```bash
curl http://localhost:8000/api/health
```

Chat:

```bash
curl -X POST http://localhost:8000/api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message":"What does this project demonstrate?","history":[]}'
```

Upload:

```bash
curl -X POST http://localhost:8000/api/documents/upload -F "file=@backend/data/documents/angular-ai-notes.md"
```

## 6. Testing

Backend unit test:

```bash
cd backend
pytest
```

Frontend build check:

```bash
cd frontend
npm install
npm run build
```

## 7. Deployment — free-friendly path

### Backend on Render

1. Push this repository to GitHub.
2. Create a new Render Web Service from the repo, or use the included `render.yaml`.
3. Set `GEMINI_API_KEY` as a secret environment variable.
4. Deploy.
5. Copy the Render URL, e.g. `https://your-api.onrender.com`.

Render currently offers free web services for testing/hobby projects, with limitations. citeturn848952search3turn848952search1

### Frontend on Netlify

1. Update `frontend/src/app/environment.ts`:

```ts
export const environment = {
  apiUrl: 'https://your-api.onrender.com/api'
};
```

2. Commit and push.
3. Import the GitHub repo into Netlify.
4. The included `netlify.toml` configures the Angular build.
5. Deploy and keep the free `netlify.app` domain or attach a custom domain later.

Netlify currently lists a $0 Free plan with deploys, custom domains/SSL, and a monthly credit limit. citeturn848952search0turn848952search2

### Important deployment note

Render free services are intended for hobby/testing use and have limitations. A sleeping backend can make the first request slow. That is normal for a free portfolio demo. citeturn848952search3

## 8. Security

Never put `GEMINI_API_KEY` in Angular code, GitHub, or browser local storage. The key belongs only in the backend environment variables.

For a public portfolio deployment, add authentication and rate limiting before allowing arbitrary users to consume the API at scale.

## 9. Production upgrade path

For interviews, explain that this demo intentionally uses a lightweight local vector store. For a larger system, replace it with PostgreSQL + pgvector or Qdrant, add authentication, background document ingestion, streaming responses, observability, evaluation, and an object store for original documents.

## 10. Resume / LinkedIn description

**AI RAG Assistant | Angular, FastAPI, Gemini, RAG**

Built a full-stack Retrieval Augmented Generation chatbot using Angular and FastAPI, implementing document ingestion, text chunking, Gemini embeddings, vector similarity search, grounded prompt construction and source-aware responses. Added PDF/Markdown/TXT upload, REST APIs, CORS, error handling, automated tests and free cloud deployment.

## 11. Interview explanation — 60 seconds

“I built a full-stack RAG assistant to move beyond a basic LLM chatbot. The Angular frontend handles the chat experience and document uploads. FastAPI receives the request, embeds the user's question, searches my vector index using cosine similarity, retrieves the most relevant document chunks, and injects them into a grounded prompt for Gemini. The response comes back with the retrieved sources so the UI can show why the answer was produced. I used a lightweight NumPy-backed vector store for the portfolio version to keep it free and simple, but the same service can be replaced by pgvector or Qdrant for production scale.”
