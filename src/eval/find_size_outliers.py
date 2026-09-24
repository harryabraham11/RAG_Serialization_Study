import json

with open("data/chunks_structured/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

scored = [(len(c["text"].split()), c) for c in chunks]

print("=== 5 LARGEST STRUCTURED CHUNKS ===")
for word_count, c in sorted(scored, key=lambda x: -x[0])[:5]:
    print(f"\n{c['chunk_id']} | paper={c['paper_id']} | type={c['chunk_type']} | words={word_count}")
    print(f"  section: {c.get('section')}")
    print(f"  preview: {c['text'][:200]}...")

print("\n\n=== 5 SMALLEST STRUCTURED CHUNKS ===")
for word_count, c in sorted(scored, key=lambda x: x[0])[:5]:
    print(f"\n{c['chunk_id']} | paper={c['paper_id']} | type={c['chunk_type']} | words={word_count}")
    print(f"  section: {c.get('section')}")
    print(f"  text: {c['text']!r}")