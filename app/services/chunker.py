import re


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150
) -> list[str]:

    # Normalize Windows line endings
    cleaned = re.sub(r"\r\n?", "\n", text).strip()

    if not cleaned:
        return []

    # Split the document into paragraphs
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", cleaned)
        if p.strip()
    ]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:

        # If a single paragraph is larger than chunk_size,
        # split that paragraph separately.
        if len(paragraph) > chunk_size:

            if current:
                chunks.append(current)
                current = ""

            start = 0

            while start < len(paragraph):
                end = start + chunk_size
                piece = paragraph[start:end].strip()

                if piece:
                    chunks.append(piece)

                if end >= len(paragraph):
                    break

                start += max(1, chunk_size - overlap)

            continue

        # Start a new chunk
        if not current:
            current = paragraph

        # Paragraph still fits in the current chunk
        elif len(current) + len(paragraph) + 2 <= chunk_size:
            current += "\n\n" + paragraph

        # Current chunk is full
        else:
            chunks.append(current)

            # Preserve the last complete paragraph when it is
            # small enough to act as useful overlap.
            previous_paragraphs = current.split("\n\n")
            tail = previous_paragraphs[-1]

            if overlap > 0 and len(tail) <= overlap:
                current = tail + "\n\n" + paragraph
            else:
                current = paragraph

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if len(chunk) > 20]