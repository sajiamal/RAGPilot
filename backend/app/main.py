from pathlib import Path
from google.genai import errors

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from app.core.config import get_settings
from app.models.schemas import ChatRequest, ChatResponse, DocumentInfo, HealthResponse, Source
from app.services.gemini_service import GeminiService
from app.services.rag_service import RAGService
from app.services.vector_store import LocalVectorStore

settings = get_settings()
store = LocalVectorStore(settings.index_path)
gemini = GeminiService(settings.gemini_api_key, settings.gemini_chat_model, settings.gemini_embed_model)
rag = RAGService(gemini, store, settings.chunk_size, settings.chunk_overlap, settings.top_k)

app = FastAPI(title="AI RAG Assistant API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data/documents")
DATA_DIR.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
def seed_knowledge_base() -> None:
    """Index the included sample document the first time the service starts."""
    if store.count > 0:
        return
    seed = DATA_DIR / "angular-ai-notes.md"
    if seed.exists():
        try:
            rag.index_document(seed.name, seed.read_text(encoding="utf-8"))
        except Exception:
            # The API remains available even when a first-run embedding call fails.
            pass


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md"}:
        return content.decode("utf-8", errors="ignore")
    if suffix == ".pdf":
        from io import BytesIO
        reader = PdfReader(BytesIO(content))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)
    raise HTTPException(status_code=400, detail="Only .txt, .md and .pdf files are supported.")


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        indexed_chunks=store.count,
        indexed_documents=len(store.document_summary()),
    )


@app.get("/api/documents", response_model=list[DocumentInfo])
def documents() -> list[DocumentInfo]:
    return [DocumentInfo(**doc) for doc in store.document_summary()]


@app.post("/api/documents/upload", response_model=DocumentInfo)
async def upload_document(file: UploadFile = File(...)) -> DocumentInfo:
    content = await file.read()
    limit = settings.max_file_size_mb * 1024 * 1024
    if len(content) > limit:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_file_size_mb} MB limit.")

    name = Path(file.filename or "document").name
    text = extract_text(name, content)
    chunk_count = rag.index_document(name, text)
    if chunk_count == 0:
        raise HTTPException(status_code=400, detail="No readable text found in the document.")
    (DATA_DIR / name).write_bytes(content)
    return DocumentInfo(name=name, chunks=chunk_count)


@app.delete("/api/documents/{name}")
def delete_document(name: str) -> dict[str, str]:
    safe_name = Path(name).name
    store.delete(safe_name)
    stored_file = DATA_DIR / safe_name
    if stored_file.exists():
        stored_file.unlink()
    return {"message": f"Deleted {safe_name}"}


@app.delete("/api/documents")
def clear_documents() -> dict[str, str]:
    store.clear()
    for path in DATA_DIR.iterdir():
        if path.is_file():
            path.unlink()
    return {"message": "All documents cleared"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        answer, sources = rag.chat(
            request.message,
            [m.model_dump() for m in request.history]
        )

        return ChatResponse(
            answer=answer,
            sources=[Source(**source) for source in sources]
        )

    except errors.APIError as exc:
        print(f"Gemini API error: {exc}")

        if exc.code == 429:
            raise HTTPException(
                status_code=429,
                detail="AI usage limit reached. Please try again later."
            ) from exc

        if exc.code == 503:
            raise HTTPException(
                status_code=503,
                detail="The AI service is temporarily busy. Please try again shortly."
            ) from exc

        raise HTTPException(
            status_code=502,
            detail="The AI service could not process your request."
        ) from exc

    except Exception as exc:
        print(f"Unexpected chat error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while processing your question."
        ) from exc
