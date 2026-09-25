import json
from pathlib import Path
from threading import Lock

import numpy as np


class LocalVectorStore:
    """Small JSON-backed vector store for a portfolio RAG demo.

    This intentionally avoids a paid/vector-database dependency. For production,
    replace this class with pgvector, Qdrant, Pinecone, etc.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self.items: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self.items = json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.items, ensure_ascii=False), encoding="utf-8")

    def add(self, document: str, chunks: list[str], embeddings: list[list[float]]) -> None:
        with self._lock:
            self.items = [item for item in self.items if item["document"] != document]
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector = np.asarray(embedding, dtype=np.float32)
                norm = float(np.linalg.norm(vector)) or 1.0
                vector = (vector / norm).tolist()
                self.items.append({"document": document, "chunk_id": i, "text": chunk, "embedding": vector})
            self._save()

    def delete(self, document: str) -> None:
        with self._lock:
            self.items = [item for item in self.items if item["document"] != document]
            self._save()

    def clear(self) -> None:
        with self._lock:
            self.items = []
            self._save()

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        if not self.items:
            return []

        query = np.asarray(query_embedding, dtype=np.float32)
        query /= max(float(np.linalg.norm(query)), 1e-12)
        matrix = np.asarray([item["embedding"] for item in self.items], dtype=np.float32)
        scores = matrix @ query
        indices = np.argsort(-scores)[:top_k]

        results = []
        for index in indices:
            item = dict(self.items[int(index)])
            item["score"] = float(scores[int(index)])
            results.append(item)
        return results

    def document_summary(self) -> list[dict]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item["document"]] = counts.get(item["document"], 0) + 1
        return [{"name": name, "chunks": count} for name, count in sorted(counts.items())]

    @property
    def count(self) -> int:
        return len(self.items)
