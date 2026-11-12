
import psycopg
from uuid import UUID, uuid4
from psycopg.types.json import Jsonb


class ConversationStore:
    """Store RAGPilot conversations and messages in PostgreSQL."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self):
        return psycopg.connect(self.database_url)

    def initialize_database(self) -> None:
        """Create the conversation tables if they do not exist."""

        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id UUID PRIMARY KEY,
                    owner_id UUID NOT NULL,
                    title TEXT NOT NULL DEFAULT 'New Chat',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_conversations_owner_updated
                ON conversations (owner_id, updated_at DESC)
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id UUID PRIMARY KEY,
                    conversation_id UUID NOT NULL
                        REFERENCES conversations(id)
                        ON DELETE CASCADE,
                    role TEXT NOT NULL
                        CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    sources JSONB NOT NULL DEFAULT '[]'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                    idx_messages_conversation_created
                ON messages (conversation_id, created_at, id)
                """
            )

            conn.commit()

    
    def create_conversation(
        self,
        owner_id: UUID,
        title: str = "New Chat",
    ) -> dict:
        """Create a conversation belonging to one visitor."""

        conversation_id = uuid4()

        with self._connect() as conn:
            row = conn.execute(
                """
                INSERT INTO conversations (
                    id,
                    owner_id,
                    title
                )
                VALUES (%s, %s, %s)
                RETURNING
                    id,
                    title,
                    created_at,
                    updated_at
                """,
                (
                    conversation_id,
                    owner_id,
                    title,
                ),
            ).fetchone()

        return {
            "id": str(row[0]),
            "title": row[1],
            "created_at": row[2].isoformat(),
            "updated_at": row[3].isoformat(),
        }


    
    def list_conversations(
        self,
        owner_id: UUID,
    ) -> list[dict]:
        """Retrieve conversations belonging to one visitor."""

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    id,
                    title,
                    created_at,
                    updated_at
                FROM conversations
                WHERE owner_id = %s
                ORDER BY updated_at DESC, id DESC
                """,
                (owner_id,),
            ).fetchall()

        return [
            {
                "id": str(row[0]),
                "title": row[1],
                "created_at": row[2].isoformat(),
                "updated_at": row[3].isoformat(),
            }
            for row in rows
        ]


    
    def add_message(
        self,
        owner_id: UUID,
        conversation_id: UUID,
        role: str,
        content: str,
        sources: list[dict] | None = None,
    ) -> dict:
        """Save a message to a conversation owned by this visitor."""

        if role not in ("user", "assistant"):
            raise ValueError("Invalid message role.")

        message_id = uuid4()

        with self._connect() as conn:
            # Confirm that this visitor owns the conversation.
            conversation = conn.execute(
                """
                SELECT id
                FROM conversations
                WHERE id = %s AND owner_id = %s
                FOR UPDATE
                """,
                (conversation_id, owner_id),
            ).fetchone()

            if conversation is None:
                raise ValueError(
                    "Conversation not found or access denied."
                )

            row = conn.execute(
                """
                INSERT INTO messages (
                    id,
                    conversation_id,
                    role,
                    content,
                    sources
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, role, content, sources, created_at
                """,
                (
                    message_id,
                    conversation_id,
                    role,
                    content,
                    Jsonb(sources if sources is not None else []),
                ),
            ).fetchone()

            conn.execute(
                """
                UPDATE conversations
                SET updated_at = NOW()
                WHERE id = %s AND owner_id = %s
                """,
                (conversation_id, owner_id),
            )

        return {
            "id": str(row[0]),
            "role": row[1],
            "content": row[2],
            "sources": row[3],
            "created_at": row[4].isoformat(),
        }


    
    def get_messages(
        self,
        owner_id: UUID,
        conversation_id: UUID,
    ) -> list[dict]:
        """Retrieve messages from a conversation owned by this visitor."""

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    m.id,
                    m.role,
                    m.content,
                    m.sources,
                    m.created_at
                FROM messages AS m
                JOIN conversations AS c
                    ON c.id = m.conversation_id
                WHERE c.id = %s
                  AND c.owner_id = %s
                ORDER BY m.created_at ASC, m.id ASC
                """,
                (conversation_id, owner_id),
            ).fetchall()

        return [
            {
                "id": str(row[0]),
                "role": row[1],
                "content": row[2],
                "sources": row[3],
                "created_at": row[4].isoformat(),
            }
            for row in rows
        ]

    def delete_conversation(
        self,
        owner_id: UUID,
        conversation_id: UUID,
    ) -> bool:
        """Delete a conversation belonging to this visitor."""

        with self._connect() as conn:
            result = conn.execute(
                """
                DELETE FROM conversations
                WHERE id = %s AND owner_id = %s
                """,
                (conversation_id, owner_id),
            )

            deleted = result.rowcount > 0

        return deleted
