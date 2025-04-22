#!/usr/bin/env python3
import os
import glob
import json
import csv
import sys

def extract_people(input_dir, output_path):
    """
    Reads JSONs with an 'entities' list,
    filters for B‑PER/I‑PER, reconstructs names,
    and writes a CSV: doc_id, person_name.
    """
    people_by_doc = {}

    for jf in glob.glob(os.path.join(input_dir, "*.json")):
        data = json.load(open(jf, encoding="utf-8"))
        doc_id = data["doc_id"]
        entities = data.get("entities", [])

        names = []
        buffer = []
        for ent in entities:
            label = ent["entity"]
            text  = ent["text"]
            # assuming labels like "B-PER", "I-PER"
            if label.endswith("PER"):
                buffer.append(text)
            else:
                if buffer:
                    names.append(" ".join(buffer))
                    buffer = []
        # catch any trailing name
        if buffer:
            names.append(" ".join(buffer))

        # de‑dupe while preserving order
        seen = set()
        unique = []
        for name in names:
            if name not in seen:
                seen.add(name)
                unique.append(name)
        people_by_doc[doc_id] = unique

    # write out to CSV
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["doc_id", "person_name"])
        for doc_id, names in people_by_doc.items():
            for name in names:
                writer.writerow([doc_id, name])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: extract_people.py <input_json_dir> <output_csv>")
        sys.exit(1)
    extract_people(sys.argv[1], sys.argv[2])
