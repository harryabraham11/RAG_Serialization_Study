import json

with open("data/chunks_structured/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

p002_chunks = [c for c in chunks if c["paper_id"] == "P002"]
# Print a window of chunks around P002_040 by their position in the list
target_index = next(i for i, c in enumerate(p002_chunks) if c["chunk_id"] == "P002_040")

for c in p002_chunks[max(0, target_index - 3): target_index + 3]:
    marker = " <-- gold table chunk" if c["chunk_id"] == "P002_040" else ""
    print(f"\n--- {c['chunk_id']} (type={c['chunk_type']}){marker} ---")
    print(c["text"][:300])