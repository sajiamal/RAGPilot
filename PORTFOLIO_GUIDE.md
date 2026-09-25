# Portfolio & Interview Guide

## Project title
**RAGPilot — Full-Stack AI Knowledge Assistant**

## One-line project description
A full-stack RAG chatbot that lets users upload documents and ask natural-language questions, using semantic retrieval and Gemini to generate grounded answers with source evidence.

## What you can say you built

I built the application end-to-end. Angular is responsible for the responsive chatbot UI, local state, document upload, and API integration. FastAPI provides REST endpoints for chat, health checks and document management. The backend extracts document text, chunks it with overlap, generates embeddings, stores normalized vectors, retrieves the top-k similar chunks with cosine similarity, and injects those chunks into a grounded Gemini prompt before returning the answer and source metadata.

## Main technologies

Angular 22, TypeScript, Signals, HttpClient, FastAPI, Python, Pydantic, Gemini API, embeddings, cosine similarity, NumPy, pypdf, REST, CORS, Docker, Pytest, Netlify, Render.

## Demo flow for recruiters

1. Open the live Angular app.
2. Show the sample knowledge-base document.
3. Ask: `What does the RAG pipeline do in this project?`
4. Show the answer and the retrieved-source panel.
5. Upload a PDF or Markdown file about another topic.
6. Ask a question whose answer is in that uploaded document.
7. Delete the document and ask the same question again to demonstrate how retrieval changes.

## Good demo questions

- What is RAG and why is it useful?
- How does this project calculate similarity?
- What technologies are used in the frontend?
- Why is the vector store JSON-backed?
- What would you change for production scale?

## Resume bullets

- Built a full-stack Retrieval Augmented Generation (RAG) chatbot using Angular 22, FastAPI and Gemini, implementing document ingestion, chunking, embeddings, vector similarity search and grounded response generation.
- Developed PDF/Markdown/TXT ingestion with top-k semantic retrieval, source-aware responses, REST APIs, CORS, environment-based secrets and error handling.
- Added a responsive Angular chatbot UI with Signals, typed API models, document management and retrieved-source visualization; prepared the application for Docker, Netlify and Render deployment.

## LinkedIn project post

I built a full-stack RAG chatbot to expand my AI development skills beyond traditional frontend work.

The project uses Angular 22 for the UI and FastAPI for the backend. Users can upload PDF/Markdown/TXT documents, which are chunked and converted into embeddings. At query time, the system performs semantic retrieval using cosine similarity and sends the most relevant context to Gemini for a grounded answer. The UI also shows the retrieved sources used for the response.

This project helped me get hands-on with RAG architecture, embeddings, vector search, prompt grounding, REST APIs, AI integration, testing and deployment.

GitHub: <add-your-repo-link>
Live demo: <add-your-live-link>

#Angular #TypeScript #Python #FastAPI #RAG #GenerativeAI #Gemini #AIEngineering #SoftwareDevelopment

## Interview questions you should prepare

### 1. What is RAG?
Retrieval Augmented Generation combines information retrieval with a generative model. Instead of asking the model to rely only on what it learned during training, the application retrieves relevant external context and gives that context to the model before generation.

### 2. Why embeddings?
Embeddings convert text into vectors where semantically similar text tends to be closer together. That allows the application to retrieve relevant information even when the user's wording does not exactly match the document wording.

### 3. Why cosine similarity?
Cosine similarity compares the angle between vectors and is commonly used for normalized embedding vectors. In the demo, normalized vectors make the similarity calculation efficient as a matrix-vector multiplication.

### 4. Why chunk documents?
Sending a whole large document on every request is inefficient and can dilute relevance. Chunking creates smaller retrieval units so the query can bring back only the most relevant passages.

### 5. Why overlap between chunks?
Overlap reduces the chance that important context is split exactly at a chunk boundary. The current demo uses a 150-character overlap by default.

### 6. Why not use a vector database?
The portfolio version is intentionally small and free. The vector-store interface isolates that decision, so it can later be replaced by PostgreSQL + pgvector, Qdrant or another production vector database without redesigning the frontend.

### 7. How do frontend and backend communicate?
Angular uses `HttpClient` to call FastAPI REST endpoints. The backend enables CORS for the frontend origin. JSON is used for chat requests/responses, while `multipart/form-data` is used for file uploads.

### 8. How would you improve this for production?
Add authentication, rate limiting, persistent object storage, a production vector database, background indexing jobs, streaming model responses, structured logging, monitoring, retrieval evaluation, prompt/version management, and better handling for multiple users and document permissions.
