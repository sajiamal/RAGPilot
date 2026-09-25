from app.core.config import get_settings
from app.services.gemini_service import GeminiService

settings = get_settings()

gemini = GeminiService(
    api_key=settings.gemini_api_key,
    chat_model=settings.gemini_chat_model,
    embed_model=settings.gemini_embed_model,
)

texts = [
    "Angular is a frontend framework.",
    "FastAPI is a Python backend framework.",
    "RAG retrieves relevant information before generating an answer."
]

embeddings = gemini.embed(texts)

print("Number of embeddings:", len(embeddings))

for index, embedding in enumerate(embeddings):
    print(f"Embedding {index}:")
    print("Number of dimensions:", len(embedding))
    print("First 5 values:", embedding[:5])
    print()