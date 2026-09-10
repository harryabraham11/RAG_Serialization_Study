from sentence_transformers import SentenceTransformer
import numpy as np
import json

QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

def load_corpus(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_dense_index(chunks, model):
    texts = [c["text"] for c in chunks]
    # normalize_embeddings=True lets us use a simple dot product as cosine similarity
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    return embeddings

def search(query, chunks, embeddings, model, top_k=5):
    query_embedding = model.encode([QUERY_INSTRUCTION + query], normalize_embeddings=True)[0]
    scores = embeddings @ query_embedding
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
    if top_k is None:
        return ranked
    return ranked[:top_k]

if __name__ == "__main__":
    corpus_path = "data/chunks_naive/chunks.json"
    chunks = load_corpus(corpus_path)

    print("Loading embedding model...")
    model = SentenceTransformer("BAAI/bge-small-en-v1.5")
    embeddings = build_dense_index(chunks, model)

    query = "What two techniques does XGBoost use to further prevent overfitting?"
    ranked = search(query, chunks, embeddings, model, top_k=None)  # full ranking this time

    for rank, (chunk, score) in enumerate(ranked[:3], start=1):
        print(f"\nRank {rank} | score={score:.3f} | paper={chunk['paper_id']} | chunk_id={chunk['chunk_id']}")
        print(chunk["text"][:300])

    for rank, (chunk, score) in enumerate(ranked, start=1):
        if "shrinkage" in chunk["text"].lower():
            print(f"\nGold chunk found at rank {rank} out of {len(ranked)} (score={score:.3f}): {chunk['chunk_id']}")
            print(chunk["text"][:300])
            break