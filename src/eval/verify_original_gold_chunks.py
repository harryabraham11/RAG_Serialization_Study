import json

with open("data/chunks_naive/chunks.json", "r", encoding="utf-8") as f:
    naive_by_id = {c["chunk_id"]: c["text"] for c in json.load(f)}
with open("data/chunks_structured/chunks.json", "r", encoding="utf-8") as f:
    structured_by_id = {c["chunk_id"]: c["text"] for c in json.load(f)}

print("--- NAIVE P002_004 ---")
print(naive_by_id.get("P002_004", "MISSING"))

print("\n--- NAIVE P002_005 ---")
print(naive_by_id.get("P002_005", "MISSING"))

print("\n--- STRUCTURED P002_005 ---")
print(structured_by_id.get("P002_005", "MISSING"))

print("\n--- CONFIRM P001_006 with the correct keyword ---")
print("'convex' in P001_006 naive:", "convex" in naive_by_id.get("P001_006", "").lower())