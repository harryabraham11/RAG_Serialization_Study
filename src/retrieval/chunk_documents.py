import os
import re
import json

def word_count(text):
    return len(text.split())


def split_long_paragraph(paragraph, target_words=200):
    words = paragraph.split()
    if len(words) <= target_words * 1.5:
        return [paragraph]
    pieces = []
    for i in range(0, len(words), target_words):
        pieces.append(" ".join(words[i:i + target_words]))
    return pieces


def split_long_table(table_lines, target_words=200, hard_cap_multiplier=3):
    """Splits a table by accumulated WORD COUNT across rows, not row count --
    a table can have very few rows but be enormous if each row is wide
    (many columns). The header + separator row are repeated at the top of
    each split piece so every piece stays a valid, self-contained table."""
    if len(table_lines) <= 2:
        return [table_lines]
    header = table_lines[:2]
    header_words = word_count(" ".join(header))
    data_rows = table_lines[2:]

    total_words = word_count(" ".join(table_lines))
    if total_words <= target_words * hard_cap_multiplier:
        return [table_lines]

    pieces = []
    current_rows = []
    current_words = header_words
    for row in data_rows:
        row_words = word_count(row)
        if current_words + row_words > target_words and current_rows:
            pieces.append(header + current_rows)
            current_rows = []
            current_words = header_words
        current_rows.append(row)
        current_words += row_words
    if current_rows:
        pieces.append(header + current_rows)

    return pieces if pieces else [table_lines]


def group_into_chunks(paragraphs, target_words=200, section=None, chunk_type="text"):
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
    merged = []
    buffer = None
    for chunk in chunks:
        if chunk["chunk_type"] == "table":
            if buffer:
                if word_count(buffer["text"]) < min_words and merged and merged[-1]["chunk_type"] != "table":
                    merged[-1]["text"] = merged[-1]["text"] + "\n\n" + buffer["text"]
                else:
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
        if word_count(buffer["text"]) < min_words and merged and merged[-1]["chunk_type"] != "table":
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

    def flush_table():
        nonlocal table_lines
        if not table_lines:
            return
        if len(table_lines) < 2:
            buffer_paragraphs.append(" ".join(table_lines).strip())
        else:
            for piece in split_long_table(table_lines, target_words=target_words):
                chunks.append({"text": "\n".join(piece), "section": current_section, "chunk_type": "table"})
        table_lines = []

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
                flush_table()
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

    if in_table:
        flush_table()
    flush_paragraph()
    flush_all_as_chunks()

    return merge_small_chunks(chunks)


def build_corpus(input_folder, chunker, output_path, target_words=200, hard_cap_multiplier=3):
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

    hard_cap = target_words * hard_cap_multiplier
    remaining_outliers = [c for c in all_chunks if word_count(c["text"]) > hard_cap]
    if remaining_outliers:
        print(f"  NOTE: {len(remaining_outliers)} chunk(s) still exceed {hard_cap} words "
              f"(a single table row too wide to split further). Avoid using these as gold chunks:")
        for c in sorted(remaining_outliers, key=lambda c: -word_count(c["text"]))[:10]:
            print(f"    {c['chunk_id']} ({word_count(c['text'])} words)")


if __name__ == "__main__":
    build_corpus("data/parsed_naive", chunk_naive_text, "data/chunks_naive/chunks.json")
    build_corpus("data/parsed_structured", chunk_structured_markdown, "data/chunks_structured/chunks.json")