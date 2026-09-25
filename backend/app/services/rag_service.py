from .chunker import chunk_text
from .gemini_service import GeminiService
from .vector_store import LocalVectorStore


class RAGService:
    def __init__(self, gemini: GeminiService, store: LocalVectorStore, chunk_size: int, overlap: int, top_k: int):
        self.gemini = gemini
        self.store = store
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.top_k = top_k

    def index_document(self, name: str, text: str) -> int:
        chunks = chunk_text(text, self.chunk_size, self.overlap)
        if not chunks:
            return 0
        embeddings = self.gemini.embed(chunks)
        self.store.add(name, chunks, embeddings)
        return len(chunks)

    def chat(self, message: str, history: list[dict]) -> tuple[str, list[dict]]:
        query_embedding = self.gemini.embed([message])[0]
        results = self.store.search(query_embedding, self.top_k)

        context = "\n\n".join(
            f"[Source: {item['document']} | chunk {item['chunk_id']} | score {item['score']:.3f}]\n{item['text']}"
            for item in results
        )
        if not context:
            context = "No documents are currently indexed."

        answer = self.gemini.answer(message, context, history)
        sources = [
            {
                "document": item["document"],
                "chunk_id": item["chunk_id"],
                "score": round(item["score"], 4),
                "preview": item["text"][:400].replace("\n", " "),
            }
            for item in results
        ]
        return answer, sources
