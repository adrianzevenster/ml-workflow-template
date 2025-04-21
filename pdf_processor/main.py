#!/usr/bin/env python3
import os
import json
import click

from scripts.db_fetch import fetch_pdf_from_db
from scripts.pdf_sanitize import split_pdf_pages
from scripts.gcs_upload import upload_to_gcs
from scripts.docai_process import process_with_document_ai
from scripts.gemini_process import extract_persons_from_text

@click.command()
@click.option("--record-id", required=True, type=int, help="DB record ID containing the PDF")
@click.option("--work-dir",  required=True,             help="Local scratch dir for outputs")
def main(record_id, work_dir):
    os.makedirs(work_dir, exist_ok=True)

    # 1. Fetch PDF
    pdf_bytes = fetch_pdf_from_db(record_id)
    print(f"✔ Fetched PDF (record {record_id}) → {len(pdf_bytes)} bytes")

    # 2. Split into pages
    pages = split_pdf_pages(pdf_bytes)
    print(f"✔ Split into {len(pages)} page(s)")

    all_text = ""
    # 3–5. Upload each page, call Document AI, accumulate text
    for i, page in enumerate(pages, start=1):
        uri = upload_to_gcs(f"records/{record_id}/page_{i}.pdf", page)
        print(f" → Uploaded page {i} to {uri}")

        doc = process_with_document_ai(page)
        print(f" → Document AI: {len(doc.entities)} entities")
        all_text += doc.text + "\n\n"

    # 6. Call Gemini (Vertex AI) for PERSON extraction
    person_lists = extract_persons_from_text(all_text)
    print("✔ Gemini PERSON extraction results:")
    for chunk_res in person_lists:
        print("  -", chunk_res)

    # 7. Write final JSON
    out_path = os.path.join(work_dir, f"{record_id}_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "record_id": record_id,
            "docai_text": all_text,
            "gemini_responses": person_lists
        }, f, ensure_ascii=False, indent=2)

    print(f"✔ Pipeline complete — output at {out_path}")

if __name__ == "__main__":
    main()
