import json

for label, path in [("naive", "data/chunks_naive/chunks.json"), ("structured", "data/chunks_structured/chunks.json")]:
    with open(path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    p001_chunks = [c for c in chunks if c["paper_id"] == "P001"]
    word_counts = [len(c["text"].split()) for c in p001_chunks]
    print(f"{label}: {len(p001_chunks)} chunks for P001")
    print(f"{label}: avg words/chunk = {sum(word_counts) / len(word_counts):.1f}, min = {min(word_counts)}, max = {max(word_counts)}")
    print()