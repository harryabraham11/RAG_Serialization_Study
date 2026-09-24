import json

EXPECTED_PAPERS = 30

for label, path in [("naive", "data/chunks_naive/chunks.json"), ("structured", "data/chunks_structured/chunks.json")]:
    with open(path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    all_paper_ids = sorted(set(c["paper_id"] for c in chunks))
    word_counts = [len(c["text"].split()) for c in chunks]

    print(f"{label}: {len(chunks)} total chunks across {len(all_paper_ids)} papers")
    if len(all_paper_ids) != EXPECTED_PAPERS:
        expected_ids = {f"P{i:03d}" for i in range(1, EXPECTED_PAPERS + 1)}
        missing = sorted(expected_ids - set(all_paper_ids))
        print(f"  WARNING: expected {EXPECTED_PAPERS} papers, found {len(all_paper_ids)}. Missing: {missing}")
    print(f"{label}: avg words/chunk = {sum(word_counts) / len(word_counts):.1f}, min = {min(word_counts)}, max = {max(word_counts)}")
    print()