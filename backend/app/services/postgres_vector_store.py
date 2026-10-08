import psycopg
from pgvector.psycopg import register_vector


class PostgresVectorStore:
    """PostgreSQL + pgvector backed vector store for RAGPilot."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self._initialize_database()

    def _connect(self):
        conn = psycopg.connect(self.database_url)
        register_vector(conn)
        return conn

    def _initialize_database(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id BIGSERIAL PRIMARY KEY,
                    document TEXT NOT NULL,
                    chunk_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    embedding VECTOR(768) NOT NULL,
                    UNIQUE (document, chunk_id)
                )
                """
            )
            conn.commit()

    def add(
        self,
        document: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings must contain the same number of items."
            )

        with self._connect() as conn:
            # Re-uploading a document replaces its existing chunks.
            conn.execute(
                "DELETE FROM document_chunks WHERE document = %s",
                (document,),
            )

            for chunk_id, (chunk, embedding) in enumerate(
                zip(chunks, embeddings)
            ):
                conn.execute(
                    """
                    INSERT INTO document_chunks
                        (document, chunk_id, text, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        document,
                        chunk_id,
                        chunk,
                        embedding,
                    ),
                )

            conn.commit()

    def delete(self, document: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM document_chunks WHERE document = %s",
                (document,),
            )
            conn.commit()

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM document_chunks")
            conn.commit()

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    document,
                    chunk_id,
                    text,
                    1 - (embedding <=> %s::vector) AS score
                FROM document_chunks
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    query_embedding,
                    query_embedding,
                    top_k,
                ),
            ).fetchall()

        return [
            {
                "document": row[0],
                "chunk_id": row[1],
                "text": row[2],
                "score": float(row[3]),
            }
            for row in rows
        ]

    def document_summary(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT document, COUNT(*)
                FROM document_chunks
                GROUP BY document
                ORDER BY document
                """
            ).fetchall()

        return [
            {
                "name": row[0],
                "chunks": row[1],
            }
            for row in rows
        ]

    @property
    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM document_chunks"
            ).fetchone()

        return int(row[0]) if row else 0