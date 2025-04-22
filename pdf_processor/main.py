#!/usr/bin/env python3
import os, json, click
from scripts.db_fetch import fetch_pdf_from_db
from scripts.pdf_sanitize import split_pdf_pages
from scripts.gcs_upload import upload_to_gcs
from scripts.docai_process import process_with_document_ai
from scripts.gemini_process import extract_persons_from_text

@click.command()
@click.option("--record-id", required=True, type=int)
@click.option("--work-dir",  required=True)
def main(record_id, work_dir):
    os.makedirs(work_dir, exist_ok=True)

    # 1) fetch PDF bytes
    pdf = fetch_pdf_from_db(record_id)
    print(f"[1] Fetched PDF ({len(pdf)} bytes)")

    # 2) split pages
    pages = split_pdf_pages(pdf)
    print(f"[2] Split into {len(pages)} pages")

    # 3) call Document AI per page, accumulate text & full doc JSON
    all_text = ""
    docai_records = []
    for i, page in enumerate(pages, start=1):
        uri = upload_to_gcs(f"records/{record_id}/page_{i}.pdf", page)
        print(f"[3.{i}] uploaded to {uri}")

        doc = process_with_document_ai(page)
        docai_records.append(json.loads(doc.to_json()))    # full JSON
        all_text += doc.text + "\n\n"

    # dump raw Document AI JSON
    docai_path = os.path.join(work_dir, "docai_raw.json")
    with open(docai_path, "w") as f:
        json.dump(docai_records, f, indent=2)
    print(f"[3] → docai_raw.json")

    # 4) call Gemini for PERSON extraction
    gemini_responses = extract_persons_from_text(all_text)
    gemini_path = os.path.join(work_dir, "gemini_raw.json")
    with open(gemini_path, "w") as f:
        json.dump(gemini_responses, f, indent=2)
    print(f"[4] → gemini_raw.json")

    # 5) write lightweight results (text + entities) if needed
    results = {
        "record_id": record_id,
        "text": all_text,
        "person_chunks": gemini_responses
    }
    out_path = os.path.join(work_dir, f"{record_id}_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[5] → {record_id}_results.json")

if __name__ == "__main__":
    main()
