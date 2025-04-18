#!/usr/bin/env python3
import os
import glob
import json
import sys
from pdfminer.high_level import extract_text

def extract_texts(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # grab everything in input_dir, case‑insensitive .pdf
    pattern = os.path.join(input_dir, "*")
    pdfs = sorted([p for p in glob.glob(pattern) if p.lower().endswith(".pdf")])

    print(f"🔍 Found {len(pdfs)} PDF(s):")
    for p in pdfs:
        print("   ", p)
    if not pdfs:
        print("⚠️  No PDF files found. Check your paths and extensions.")
        return

    for pdf_path in pdfs:
        text = extract_text(pdf_path)
        base = os.path.basename(pdf_path)                # e.g. "invoice_01.pdf"
        out_name = f"{base}.json"                        # e.g. "invoice_01.pdf.json"
        out_path = os.path.join(output_dir, out_name)

        print(f"✏️  Writing → {out_path} ({len(text)} chars)")
        with open(out_path, "w") as f:
            json.dump({"doc_id": base, "text": text}, f)

def main():
    if len(sys.argv) != 3:
        print("Usage: extract_text.py INPUT_DIR OUTPUT_DIR")
        sys.exit(1)
    extract_texts(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
