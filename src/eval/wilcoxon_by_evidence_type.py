import pandas as pd
from scipy.stats import wilcoxon

df = pd.read_csv("results/evaluation_results.csv")

print("=" * 70)
print("WILCOXON SIGNED-RANK TEST: naive vs structured, per evidence_type x retriever")
print("=" * 70)

for evidence_type in df["evidence_type"].unique():
    for retriever in df["retriever"].unique():
        sub = df[(df["evidence_type"] == evidence_type) & (df["retriever"] == retriever)]

        naive = sub[sub["corpus_condition"] == "naive"].set_index("question_id")["reciprocal_rank"]
        structured = sub[sub["corpus_condition"] == "structured"].set_index("question_id")["reciprocal_rank"]

        paired = pd.concat([naive, structured], axis=1, keys=["naive", "structured"]).dropna()
        diffs = paired["naive"] - paired["structured"]
        n_pairs = len(paired)
        n_nonzero = (diffs != 0).sum()

        print(f"\n--- {evidence_type} / {retriever} ---")
        print(f"n pairs = {n_pairs}, n nonzero = {n_nonzero}")
        print(f"mean naive MRR = {paired['naive'].mean():.4f}, mean structured MRR = {paired['structured'].mean():.4f}")

        if n_nonzero < 1:
            print("All differences zero -- cannot run test.")
            continue

        stat, p_value = wilcoxon(paired["naive"], paired["structured"])
        r = 1 - (2 * stat) / (n_nonzero * (n_nonzero + 1))
        print(f"Wilcoxon statistic = {stat:.4f}, p-value = {p_value:.6f}, effect size r = {r:.4f}")