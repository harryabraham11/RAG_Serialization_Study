import json

CORPUS_PATH = "data/chunks_structured/chunks.json"  # switch to chunks_structured/chunks.json when needed
PAPER_ID = "P001"
KEYWORD = "shrinkage"

with open(CORPUS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

matches = [c for c in chunks if c["paper_id"] == PAPER_ID and KEYWORD.lower() in c["text"].lower()]
print(f"Found {len(matches)} chunk(s) mentioning '{KEYWORD}' in {PAPER_ID} ({CORPUS_PATH}):\n")
for c in matches:
    print(f"--- {c['chunk_id']} ({len(c['text'].split())} words) ---")
    print(c["text"])
    print()