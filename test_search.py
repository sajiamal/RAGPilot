from app.core.config import get_settings
from app.services.gemini_service import GeminiService
from app.services.vector_store import LocalVectorStore


settings = get_settings()

gemini = GeminiService(
    api_key=settings.gemini_api_key,
    chat_model=settings.gemini_chat_model,
    embed_model=settings.gemini_embed_model,
)

store = LocalVectorStore(settings.index_path)

question = "Which production vector databases can replace the local JSON vector store?"

query_embedding = gemini.embed([question])[0]

results = store.search(query_embedding, top_k=5)

print("Question:", question)
print()

for result in results:
    print("Document:", result["document"])
    print("Chunk:", result["chunk_id"])
    print("Score:", result["score"])
    print("Preview:", result["text"][:400])
    print("-" * 60)