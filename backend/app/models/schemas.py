from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list)


class Source(BaseModel):
    document: str
    chunk_id: int
    score: float
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class DocumentInfo(BaseModel):
    name: str
    chunks: int


class HealthResponse(BaseModel):
    status: str
    indexed_chunks: int
    indexed_documents: int
