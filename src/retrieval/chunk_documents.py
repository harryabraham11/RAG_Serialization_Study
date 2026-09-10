import os
import re
import json

def word_count(text):
    return len(text.split())


def split_long_paragraph(paragraph, target_words=200):
    """If a single paragraph is already much bigger than our target chunk size
    (common in naive PDF text with few/no blank lines), break it into
    fixed-size word windows so it doesn't become one giant chunk."""
    words = paragraph.split()
    if len(words) <= target_words * 1.5:
        return [paragraph]
    pieces = []
    for i in range(0, len(words), target_words):
        pieces.append(" ".join(words[i:i + target_words]))
    return pieces


def group_into_chunks(paragraphs, target_words=200, section=None, chunk_type="text"):
    # First, break up any paragraph that's already oversized on its own
    expanded = []
    for para in paragraphs:
        expanded.extend(split_long_paragraph(para, target_words=target_words))

    chunks = []
    current = []
    current_words = 0
    for para in expanded:
        para_words = word_count(para)
        if current_words + para_words > target_words and current:
            chunks.append({"text": "\n\n".join(current), "section": section, "chunk_type": chunk_type})
            current = []
            current_words = 0
        current.append(para)
        current_words += para_words
    if current:
        chunks.append({"text": "\n\n".join(current), "section": section, "chunk_type": chunk_type})
    return chunks


def merge_small_chunks(chunks, min_words=60):
    """Folds any undersized 'text' chunk into the next chunk, so we don't end up
    with tiny orphan chunks near section headings. Tables are never touched."""
    merged = []
    buffer = None
    for chunk in chunks:
        if chunk["chunk_type"] == "table":
            if buffer:
                merged.append(buffer)
                buffer = None
            merged.append(chunk)
            continue
        if buffer is None:
            buffer = dict(chunk)
        else:
            buffer["text"] = buffer["text"] + "\n\n" + chunk["text"]
        if word_count(buffer["text"]) >= min_words:
            merged.append(buffer)
            buffer = None
    if buffer:
        if merged and merged[-1]["chunk_type"] != "table":
            merged[-1]["text"] = merged[-1]["text"] + "\n\n" + buffer["text"]
        else:
            merged.append(buffer)
    return merged


def chunk_naive_text(text, target_words=200):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = group_into_chunks(paragraphs, target_words=target_words, section=None, chunk_type="text")
    return merge_small_chunks(chunks)


def chunk_structured_markdown(text, target_words=200, min_flush_words=80):
    lines = text.split("\n")
    chunks = []
    current_section = None
    buffer_paragraphs = []
    buffer_lines = []
    table_lines = []
    in_table = False

    def flush_paragraph():
        if buffer_lines:
            buffer_paragraphs.append(" ".join(buffer_lines).strip())
            buffer_lines.clear()

    def buffered_words():
        return sum(word_count(p) for p in buffer_paragraphs)

    def flush_all_as_chunks():
        nonlocal buffer_paragraphs
        if buffer_paragraphs:
            chunks.extend(group_into_chunks(buffer_paragraphs, target_words=target_words,
                                             section=current_section, chunk_type="text"))
            buffer_paragraphs = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("|"):
            if not in_table:
                flush_paragraph()
                in_table = True
            table_lines.append(line)
            continue
        else:
            if in_table:
                chunks.append({"text": "\n".join(table_lines), "section": current_section, "chunk_type": "table"})
                table_lines = []
                in_table = False

        if stripped.startswith("#"):
            flush_paragraph()
            if buffered_words() >= min_flush_words:
                flush_all_as_chunks()
            current_section = stripped.lstrip("#").strip()
            continue

        if stripped == "":
            flush_paragraph()
            continue

        buffer_lines.append(stripped)

    if in_table and table_lines:
        chunks.append({"text": "\n".join(table_lines), "section": current_section, "chunk_type": "table"})
    flush_paragraph()
    flush_all_as_chunks()

    return merge_small_chunks(chunks)


def build_corpus(input_folder, chunker, output_path):
    all_chunks = []
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".txt") or filename.endswith(".md"):
            paper_id = filename.split(".")[0]
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                text = f.read()

            paper_chunks = chunker(text)
            for i, chunk in enumerate(paper_chunks):
                all_chunks.append({
                    "chunk_id": f"{paper_id}_{i:03d}",
                    "paper_id": paper_id,
                    "chunk_index": i,
                    **chunk
                })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_chunks)} chunks to {output_path}")


if __name__ == "__main__":
    build_corpus("data/parsed_naive", chunk_naive_text, "data/chunks_naive/chunks.json")
    build_corpus("data/parsed_structured", chunk_structured_markdown, "data/chunks_structured/chunks.json")