import pandas as pd

df = pd.read_csv("results/evaluation_results.csv")  # adjust path to wherever your CSV lives

# --- 1. Overall summary: mean MRR and Hit@k per (corpus_condition, retriever) ---
overall = (
    df.groupby(["corpus_condition", "retriever"])
    .agg(
        mean_mrr=("reciprocal_rank", "mean"),
        std_mrr=("reciprocal_rank", "std"),
        hit_at_1=("hit_at_1", "mean"),
        hit_at_3=("hit_at_3", "mean"),
        hit_at_5=("hit_at_5", "mean"),
        n=("reciprocal_rank", "count"),
    )
    .round(4)
    .reset_index()
)

print("=" * 70)
print("OVERALL: mean MRR and Hit@k by corpus_condition x retriever")
print("=" * 70)
print(overall.to_string(index=False))

# --- 2. Breakdown by evidence_type (text / table / equation) ---
by_evidence = (
    df.groupby(["evidence_type", "corpus_condition", "retriever"])
    .agg(
        mean_mrr=("reciprocal_rank", "mean"),
        hit_at_1=("hit_at_1", "mean"),
        hit_at_3=("hit_at_3", "mean"),
        hit_at_5=("hit_at_5", "mean"),
        n=("reciprocal_rank", "count"),
    )
    .round(4)
    .reset_index()
)

print("\n" + "=" * 70)
print("BY EVIDENCE TYPE: mean MRR and Hit@k")
print("=" * 70)
print(by_evidence.to_string(index=False))

# --- 3. Save both to CSV for pasting into the paper / spreadsheet ---
overall.to_csv("data/summary_overall.csv", index=False)
by_evidence.to_csv("data/summary_by_evidence_type.csv", index=False)
print("\nSaved: data/summary_overall.csv and data/summary_by_evidence_type.csv")