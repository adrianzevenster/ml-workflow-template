#!/usr/bin/env python3
import json
import click
from google.cloud import aiplatform
from vertexai.language_models import TextGenerationModel

@click.command()
@click.argument("docai_json",      type=click.Path(exists=True))
@click.argument("gemini_json",     type=click.Path(exists=True))
@click.argument("out_path",        type=click.Path())
@click.option("--required-fields", type=str, multiple=True,
              help="Entity types that must be present for format alignment")
def main(docai_json, gemini_json, out_path, required_fields):
    # 1) Load Document AI raw output
    pages = json.load(open(docai_json, encoding="utf-8"))
    # Flatten and categorize entities
    entity_map = {}
    for page in pages:
        for ent in page.get("entities", []):
            typ = ent.get("type")
            txt = ent.get("mentionText") or ent.get("textAnchor", {}).get("content", "")
            entity_map.setdefault(typ, []).append(txt)
    # Deduplicate
    entity_map = {k: list(dict.fromkeys(v)) for k, v in entity_map.items()}

    # 2) Verification: check required fields
    missing = [f for f in required_fields if f not in entity_map]
    verification = {
        "passed": len(missing) == 0,
        "missing_fields": missing
    }

    # 3) Load raw Gemini responses (list of chunk‑level strings)
    person_chunks = json.load(open(gemini_json, encoding="utf-8"))

    # 4) Forgery detection via Gemini LLM
    aiplatform.init()  # uses env PROJECT & LOCATION
    model = TextGenerationModel.from_pretrained()
    prompt = (
        "You are a forensic document examiner. "
        "Based on the extracted entities and the full text snippet, "
        "determine whether the document shows signs of forgery or tampering, "
        "and explain your reasoning.\n\n"
        f"Entities: {entity_map}\n\n"
        f"Text Snippet: {pages[0].get('text','')[:500]}..."
    )
    forgery_resp = model.predict(prompt).text.strip()

    # 5) Decision logic: human review needed if format failed or forgery suspected
    no_forgery_phrase = "no signs of forgery"
    needs_review = (not verification["passed"]) or (no_forgery_phrase not in forgery_resp.lower())

    # 6) Consolidate analysis
    analysis = {
        "entities": entity_map,
        "verification": verification,
        "person_extraction": person_chunks,
        "forgery_assessment": forgery_resp,
        "needs_human_intervention": needs_review
    }

    # 7) Write out JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    print(f"→ analysis written to {out_path}")
    print(f"→ needs_human_intervention = {needs_review}")

if __name__ == "__main__":
    main()
