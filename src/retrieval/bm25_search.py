import json
from rank_bm25 import BM25Okapi

def load_corpus(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def tokenize(text):
    # BM25 works on individual words ("tokens"). This is the simplest possible
    # tokenizer: lowercase everything, split on whitespace. Good enough to start.
    return text.lower().split()

def build_bm25_index(chunks):
    tokenized_corpus = [tokenize(c["text"]) for c in chunks]
    return BM25Okapi(tokenized_corpus)

def search(bm25, chunks, query, top_k=5):
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]

if __name__ == "__main__":
    # Try this against "data/chunks_structured/chunks.json" too, and compare.
    corpus_path = "data/chunks_structured/chunks.json"
    chunks = load_corpus(corpus_path)
    bm25 = build_bm25_index(chunks)

    query = "What two techniques does XGBoost use to further prevent overfitting?"
    results = search(bm25, chunks, query, top_k=3)

    for rank, (chunk, score) in enumerate(results, start=1):
        print(f"\nRank {rank} | score={score:.3f} | paper={chunk['paper_id']} | chunk_id={chunk['chunk_id']}")
        print(chunk["text"][:300])

        # Diagnostic: where does the actual gold-answer chunk rank, even if it's outside top 3?
    all_scored = sorted(zip(chunks, bm25.get_scores(tokenize(query))), key=lambda x: x[1], reverse=True)
    for rank, (chunk, score) in enumerate(all_scored, start=1):
        if "shrinkage" in chunk["text"].lower():
            print(f"\nGold chunk found at rank {rank} (score={score:.3f}): {chunk['chunk_id']}")
            print(chunk["text"][:300])
            break
    else:
        print("\nNo chunk in this corpus contains the word 'shrinkage' at all.")