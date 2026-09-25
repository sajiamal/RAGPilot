from app.services.chunker import chunk_text


def test_chunk_text_creates_chunks():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = chunk_text(text, chunk_size=30, overlap=5)
    assert chunks
    assert all(chunk.strip() for chunk in chunks)
