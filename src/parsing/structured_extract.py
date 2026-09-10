from docling.document_converter import DocumentConverter
import os

INPUT_FOLDER = "data/raw_pdfs"
OUTPUT_FOLDER = "data/parsed_structured"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Create the converter once, outside the loop — it loads AI models internally,
# so reusing it for all 5 PDFs is much faster than recreating it each time
converter = DocumentConverter()

for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(INPUT_FOLDER, filename)
        print(f"Processing {filename}... (this can take a minute or two per paper)")

        # This is where the real work happens: layout detection,
        # table structure recovery, reading-order reconstruction
        result = converter.convert(pdf_path)

        # Markdown preserves headings and renders tables as proper | | | tables
        markdown_text = result.document.export_to_markdown()

        output_filename = filename.replace(".pdf", ".md")
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        print(f"Saved to {output_path}")

print("Done! All PDFs processed with structure-aware parsing.")