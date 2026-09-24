# Lost in Serialization: How Document Parsing Affects Scientific RAG Retrieval

A controlled pilot study measuring how PDF-to-text serialization quality affects retrieval performance in a Retrieval-Augmented Generation (RAG) pipeline over scientific ML papers, across three retrieval strategies (BM25, dense, hybrid) and three evidence types (text, table, equation).

## Research Question

How does document parsing/serialization quality interact with retrieval strategy and query evidence type in scientific RAG? Specifically: does a modern layout-aware parser (Docling) actually improve retrieval over a naive text-flattening extractor (PyMuPDF), and does that answer depend on what kind of evidence a question needs?

## Key Findings (pilot, n=5 papers)

This is a small pilot, not a large-scale benchmark — see Limitations below — but it surfaced concrete, mechanism-level findings:

- **Structure-aware parsing can *hurt* table retrieval.** Docling produced cleaner-looking tables but sometimes separated a table from its identifying caption into a different chunk, making it unretrievable by a question that references the table by name. MRR for table questions dropped from 0.40 (naive, BM25) to 0.06 (structured, BM25).
- **Naive extraction can silently corrupt equations.** PyMuPDF's naive text extraction turned a summation symbol (Σ) into the literal letter "X" in XGBoost's regularized objective — a font-encoding artifact, not a formatting quirk.
- **Structure-aware parsing can fail open on formulas.** Docling replaced an undecodable equation with a `<!-- formula-not-decoded -->` placeholder, losing the content entirely — while the naive extractor, by coincidence, preserved the same formula's Unicode math characters correctly.
- **Hybrid retrieval (Reciprocal Rank Fusion) is not a free win.** It improved results for equation questions but *underperformed* the better single retriever for several text and table questions, when the two retrievers' quality was highly asymmetric.

## Results Summary (Mean Reciprocal Rank, averaged over 5 papers)

| Evidence type | Parsing | BM25 | Dense | Hybrid (RRF) |
|---|---|---|---|---|
| Text | Naive | 0.69 | 0.07 | 0.30 |
| Text | Structured | 0.80 | 0.64 | 0.54 |
| Table | Naive | 0.40 | 0.81 | 0.70 |
| Table | Structured | 0.06 | 0.12 | 0.10 |
| Equation | Naive | 0.20 | 0.51 | 0.55 |
| Equation | Structured | 0.19 | 0.37 | 0.58 |

## Repository Structure

```
├── data/
│   ├── raw_pdfs/            # Source papers (see Reproduction below for links)
│   ├── parsed_naive/        # PyMuPDF text extraction output
│   ├── parsed_structured/   # Docling markdown extraction output
│   ├── chunks_naive/        # Chunked naive corpus (retrieval-ready)
│   └── chunks_structured/   # Chunked structured corpus (retrieval-ready)
├── questions/
│   └── questions.json       # 15 hand-verified questions with gold chunk IDs
├── src/
│   ├── parsing/               # PDF -> text/markdown extraction scripts
│   ├── retrieval/             # Chunking, BM25, and dense retrieval scripts
│   └── eval/                  # Full evaluation pipeline + gold-chunk verification tools
├── results/
│   └── evaluation_results.csv # Full 90-row evaluation matrix (15 questions x 2 corpora x 3 retrievers)
├── requirements.txt
└── README.md
```

## Reproducing This Project

1. Create the environment: `conda create -n rag-study python=3.11 -y && conda activate rag-study`
2. Install dependencies: `pip install -r requirements.txt`
3. Download the 5 source papers into `data/raw_pdfs/` (XGBoost: arxiv.org/pdf/1603.02754, Mamba: arxiv.org/pdf/2312.00752, DINOv2: arxiv.org/pdf/2304.07193, LoRA: arxiv.org/pdf/2106.09685, DreamerV3: arxiv.org/pdf/2301.04104), named `P001.pdf` through `P005.pdf` respectively
4. Run extraction: `python src/parsing/naive_extract.py` and `python src/parsing/structured_extract.py`
5. Run chunking: `python src/retrieval/chunk_documents.py`
6. Run the full evaluation: `python src/eval/eval_full.py`
7. Results land in `results/evaluation_results.csv`

## Limitations

- Pilot scale only: 5 papers, 15 questions. Results are illustrative and mechanism-level, not statistically powered.
- Closely related, larger-scale work exists: [OHR-Bench (ICCV 2025)](https://arxiv.org/abs/2412.02592) evaluates OCR/parsing quality's effect on RAG across 7 domains and 8,500+ pages. This project is scoped narrower and differently — specifically contrasting a text-flattening extractor against a modern layout-aware parser on scientific ML literature, with a focus on the retrieval-strategy interaction and detailed qualitative failure-mode analysis.

## Author

Harry Abraham H — final-year AIML student. Built as a final-year project and IEEE submission pilot study.
