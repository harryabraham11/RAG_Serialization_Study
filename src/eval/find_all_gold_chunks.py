import json

with open("data/chunks_naive/chunks.json", "r", encoding="utf-8") as f:
    naive_chunks = json.load(f)
with open("data/chunks_structured/chunks.json", "r", encoding="utf-8") as f:
    structured_chunks = json.load(f)

naive_by_id = {c["chunk_id"]: c for c in naive_chunks}
structured_by_id = {c["chunk_id"]: c for c in structured_chunks}

print("=== 1. P026 text: search 'combine the advantages' ===")
for corpus_name, chunks in [("NAIVE", naive_chunks), ("STRUCTURED", structured_chunks)]:
    for c in chunks:
        if c["paper_id"] == "P026" and "combine the advantages" in c["text"].lower():
            print(f"  {corpus_name} {c['chunk_id']}: {c['text'][:300]}")

print("\n=== 2. P027 text naive: search 'define internal covariate shift' ===")
for c in naive_chunks:
    if c["paper_id"] == "P027" and "define internal covariate shift" in c["text"].lower():
        print(f"  NAIVE {c['chunk_id']}: {c['text'][:300]}")

print("\n=== 3. P027 table verify: naive P027_030 full text ===")
if "P027_030" in naive_by_id:
    print(naive_by_id["P027_030"]["text"])

print("\n=== 4. P027 equation structured: search 'for each activation' ===")
for c in structured_chunks:
    if c["paper_id"] == "P027" and "for each activation" in c["text"].lower():
        print(f"  STRUCTURED {c['chunk_id']}: {c['text'][:300]}")

print("\n=== 5. P028 equation: search 'gains' + 'biases' ===")
for corpus_name, chunks in [("NAIVE", naive_chunks), ("STRUCTURED", structured_chunks)]:
    for c in chunks:
        if c["paper_id"] == "P028" and "gains" in c["text"].lower() and "biases" in c["text"].lower():
            print(f"  {corpus_name} {c['chunk_id']}: {c['text'][:300]}")

print("\n=== 6. P029 table naive: search 'Nvidia MLPerf' ===")
for c in naive_chunks:
    if c["paper_id"] == "P029" and "nvidia mlperf" in c["text"].lower():
        print(f"  NAIVE {c['chunk_id']} ({len(c['text'].split())}w): {c['text'][:400]}")

print("\n=== 7. P029 equation: search 'HBM accesses, while' ===")
for corpus_name, chunks in [("NAIVE", naive_chunks), ("STRUCTURED", structured_chunks)]:
    for c in chunks:
        if c["paper_id"] == "P029" and "hbm accesses" in c["text"].lower() and "theorem 2" in c["text"].lower():
            print(f"  {corpus_name} {c['chunk_id']}: {c['text'][:400]}")

print("\n=== 8. P030 table naive: search 'LaMDA' ===")
for c in naive_chunks:
    if c["paper_id"] == "P030" and "lamda" in c["text"].lower():
        print(f"  NAIVE {c['chunk_id']} ({len(c['text'].split())}w): {c['text'][:400]}")

print("\n=== 9. P030 equation naive: search 'functional form' ===")
for c in naive_chunks:
    if c["paper_id"] == "P030" and "functional form" in c["text"].lower():
        print(f"  NAIVE {c['chunk_id']}: {c['text'][:400]}")