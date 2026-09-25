from app.services.chunker import chunk_text

text = """
RAGPilot is a full-stack AI application.

The frontend is built using Angular and TypeScript.

The backend is built using Python and FastAPI.

The application uses Gemini for embeddings and AI generation.

The RAG pipeline retrieves relevant information from documents
before generating an answer.
"""

chunks = chunk_text(text, chunk_size=100, overlap=20)

print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks):
    print("\n--- Chunk", index, "---")
    print(chunk)