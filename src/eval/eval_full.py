import json
import csv
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "
RRF_K = 60  # standard constant from the original Reciprocal Rank Fusion paper

def tokenize(text):
    return text.lower().split()

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def best_rank(ranked_chunk_ids, gold_ids):
    for i, cid in enumerate(ranked_chunk_ids, start=1):
        if cid in gold_ids:
            return i
    return None

def rrf_fuse(ranked_lists, k=RRF_K):
    """Combines multiple ranked lists of chunk_ids into one fused ranking using Reciprocal Rank Fusion."""
    scores = {}
    for ranked_ids in ranked_lists:
        for rank, cid in enumerate(ranked_ids, start=1):
            scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank)
    return sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)

def main():
    questions = load_json("questions/questions.json")

    conditions = {
        "naive": "data/chunks_naive/chunks.json",
        "structured": "data/chunks_structured/chunks.json",
    }

    print("Loading embedding model...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")

    results = []

    for condition_name, chunks_path in conditions.items():
        print(f"\n=== Processing {condition_name} corpus ===")
        chunks = load_json(chunks_path)

        tokenized_corpus = [tokenize(c["text"]) for c in chunks]
        bm25 = BM25Okapi(tokenized_corpus)

        print("Encoding chunks for dense retrieval...")
        texts = [c["text"] for c in chunks]
        chunk_embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

        gold_field = f"gold_chunk_ids_{condition_name}"

        for q in questions:
            gold_ids = set(q[gold_field])
            query = q["question"]

            bm25_scores = bm25.get_scores(tokenize(query))
            bm25_ranked_indices = sorted(range(len(chunks)), key=lambda i: bm25_scores[i], reverse=True)
            bm25_ranked_ids = [chunks[i]["chunk_id"] for i in bm25_ranked_indices]

            query_embedding = model.encode([QUERY_INSTRUCTION + query], normalize_embeddings=True)[0]
            dense_scores = chunk_embeddings @ query_embedding
            dense_ranked_indices = np.argsort(-dense_scores)
            dense_ranked_ids = [chunks[i]["chunk_id"] for i in dense_ranked_indices]

            hybrid_ranked_ids = rrf_fuse([bm25_ranked_ids, dense_ranked_ids])

            for retriever_name, ranked_ids in [
                ("bm25", bm25_ranked_ids),
                ("dense", dense_ranked_ids),
                ("hybrid", hybrid_ranked_ids),
            ]:
                rank = best_rank(ranked_ids, gold_ids)
                results.append({
                    "question_id": q["question_id"],
                    "paper_id": q["paper_id"],
                    "evidence_type": q["evidence_type"],
                    "corpus_condition": condition_name,
                    "retriever": retriever_name,
                    "rank": rank if rank is not None else "",
                    "reciprocal_rank": round(1.0 / rank, 4) if rank else 0,
                    "hit_at_1": int(rank == 1) if rank else 0,
                    "hit_at_3": int(rank is not None and rank <= 3),
                    "hit_at_5": int(rank is not None and rank <= 5),
                })

    output_path = "results/evaluation_results.csv"
    fieldnames = ["question_id", "paper_id", "evidence_type", "corpus_condition", "retriever",
                  "rank", "reciprocal_rank", "hit_at_1", "hit_at_3", "hit_at_5"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved {len(results)} result rows to {output_path}")

if __name__ == "__main__":
    main()