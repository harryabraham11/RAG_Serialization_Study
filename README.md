# Lost in Serialization: How PDF Parsing Strategy Affects RAG Retrieval Quality

An empirical study comparing **naive text extraction** against **structure-aware parsing (Docling)** for Retrieval-Augmented Generation (RAG) pipelines, evaluated across a gold-annotated benchmark of 30 machine learning research papers.

## Key Finding

PDF parsing strategy does **not** affect RAG retrieval uniformly across content types. Structure-aware parsing catastrophically degrades **table** retrieval (MRR drops from ~0.45–0.59 to ~0.09–0.20; Wilcoxon *p* < 0.0002, effect size *r* > 0.92 across all retrievers) while leaving **text** and **equation** retrieval statistically unaffected (*p* > 0.38). However, six confirmed cases show that structure-aware parsing can silently discard entire equations — replacing them with a `<!-- formula-not-decoded -->` placeholder — while the corrupted chunk is *still retrieved successfully, including at rank 1*, by every retriever tested. This demonstrates that retrieval metrics alone (MRR, Hit@k) cannot detect a real and reproducible class of content-fidelity failure.

## Benchmark Overview

- **30 papers**, organized into 6 thematic domains (5 papers each): foundational architectures, NLP, computer vision, reinforcement learning, generative models, and systems/optimization
- **88 gold-annotated questions** (30 text, 28 table, 30 equation), each independently grounded against the original source PDF and paired with a verified gold-chunk ID in both parsing conditions
- **Two independent parsed corpora** per paper: naive (PyMuPDF, linear character-stream extraction) and structured (Docling, layout- and table-structure-aware)
- **Three retrieval methods**: BM25 (`rank_bm25`), dense retrieval (`BAAI/bge-small-en-v1.5`), and hybrid (Reciprocal Rank Fusion, k=60)

## Repository Structure

```
├── data/
│   ├── raw_pdfs/                  # Source PDFs (30 papers)
│   ├── parsed_naive/              # PyMuPDF text extraction output
│   ├── parsed_structured/         # Docling Markdown output
│   ├── chunks_naive/chunks.json   # Naive corpus, chunked (2,051 chunks)
│   ├── chunks_structured/chunks.json  # Structured corpus, chunked (2,561 chunks)
│   ├── summary_overall.csv        # Aggregate MRR/Hit@k by corpus x retriever
│   └── summary_by_evidence_type.csv   # Breakdown by text/table/equation
├── questions/
│   └── questions.json             # 88 gold-annotated questions with verified chunk IDs
├── results/
│   └── evaluation_results.csv     # Full per-question retrieval results (528 rows)
├── src/
│   ├── retrieval/
│   │   └── chunk_documents.py     # Word-budget chunking pipeline (both corpora)
│   └── eval/
│       ├── find_all_gold_chunks.py        # Gold-chunk search/verification tool
│       ├── verify_original_gold_chunks.py # Verifies original 5-paper gold chunks
│       ├── inspect_chunks.py              # Corpus-wide chunk/paper sanity checks
│       ├── find_size_outliers.py          # Flags oversized/undersized chunks
│       ├── aggregate_results.py           # Computes mean MRR/Hit@k summaries
│       └── wilcoxon_by_evidence_type.py   # Statistical significance testing
└── README.md
```

## Methodology Summary

1. **Parsing** — Each PDF is converted independently via PyMuPDF (naive) and Docling (structured), producing two full-text representations differing only in parsing strategy.
2. **Chunking** — A shared word-budget chunker (200-word target, 60-word minimum merge threshold, 600-word table hard cap with row-boundary splitting) processes both corpora identically.
3. **Gold-chunk annotation** — Each of the 88 questions is manually grounded against the original paper and matched to its supporting chunk ID(s) in both corpora via targeted search and full-text verification.
4. **Retrieval** — BM25, dense (BGE embeddings), and hybrid (RRF, k=60) rankings are computed for every question against both corpora.
5. **Evaluation** — Mean Reciprocal Rank (MRR) and Hit@1/3/5 are computed per question, then aggregated overall and stratified by evidence type (text/table/equation).
6. **Significance testing** — Paired Wilcoxon signed-rank tests (per retriever, per evidence type) with Bonferroni correction for the resulting 9 comparisons.

## Reproducing the Results

```bash
# 1. Chunk both parsed corpora
python src/retrieval/chunk_documents.py

# 2. Run the full evaluation (BM25 + dense + hybrid, both corpora, all 88 questions)
python src/eval/eval_full.py

# 3. Aggregate results
python src/eval/aggregate_results.py

# 4. Run significance tests
python src/eval/wilcoxon_by_evidence_type.py
```

## Known Corpus Limitations

- Two papers (VAE, Adam) contain no genuine numeric results table in their original publication — both report results exclusively via learning-curve figures — and are therefore evaluated on text and equation evidence only.
- Gold-chunk annotation was performed by a single annotator with AI-assisted search and verification tooling, not multiple independent annotators with inter-annotator agreement measurement.

## Citation

If you use this benchmark, please cite:

```bibtex
@inproceedings{lostinserialization2026,
  title={Lost in Serialization: How PDF Parsing Strategy Affects RAG Retrieval Quality},
  author={[Author names -- to be finalized at publication]},
  year={2026},
  note={Under review}
}
```

## License

[Specify a license here -- e.g., MIT for code, CC-BY for the question bank/annotations -- before making this repository public for review]

## Authors

Harry Abraham H, Devesh Sai Pandian Govindaraj — St. Joseph's College of Engineering, OMR, Chennai, India
Advised by Dr. Ancy Stephen (Associate Professor) and Mrs. Umayal A. R. (Assistant Professor)
