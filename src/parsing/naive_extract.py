import fitz  # this is PyMuPDF's import name
import os

# Folder where your PDFs are
INPUT_FOLDER = "data/raw_pdfs"
# Folder where extracted text will be saved
OUTPUT_FOLDER = "data/parsed_naive"

# Make sure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Go through every PDF in the input folder, one at a time
for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(INPUT_FOLDER, filename)
        print(f"Processing {filename}...")

        # Open the PDF
        doc = fitz.open(pdf_path)

        # This will hold all the text from every page
        full_text = ""

        # Go through each page and pull out its text
        for page in doc:
            full_text += page.get_text()
            full_text += "\n\n"  # blank line between pages

        doc.close()

        # Save the extracted text as a .txt file with the same name
        output_filename = filename.replace(".pdf", ".txt")
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        print(f"Saved to {output_path}")

print("Done! All PDFs processed.")