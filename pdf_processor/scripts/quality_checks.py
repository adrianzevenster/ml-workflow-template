#!/usr/bin/env python3
import json, sys, click

@click.command()
@click.argument("docai_json",      type=click.Path(exists=True))
@click.argument("gemini_json",     type=click.Path(exists=True))
@click.argument("analysis_json",   type=click.Path(exists=True))
@click.argument("out_metrics",     type=click.Path())
@click.option("--min-text-length", type=int, default=100,
              help="Minimum total text length per document")
@click.option("--min-entities",    type=int, default=1,
              help="Minimum number of total entities")
def main(docai_json, gemini_json, analysis_json, out_metrics,
         min_text_length, min_entities):
    """
    Performs data quality and output checks, then writes metrics.json.
    """

    # 1) Load inputs
    pages       = json.load(open(docai_json,    encoding="utf-8"))
    gemini_resp = json.load(open(gemini_json,   encoding="utf-8"))
    analysis    = json.load(open(analysis_json, encoding="utf-8"))

    # 2) Quality checks on Document AI
    total_pages      = len(pages)
    text_lengths     = [len(p.get("text","")) for p in pages]
    empty_pages      = sum(1 for l in text_lengths if l < min_text_length)
    total_entities   = sum(len(p.get("entities",[])) for p in pages)

    # 3) Output checks on final analysis
    has_needs_flag   = isinstance(analysis.get("needs_human_intervention"), bool)
    passed_verif     = analysis.get("verification",{}).get("passed", False)
    missing_fields   = analysis.get("verification",{}).get("missing_fields", [])

    # 4) Gem‑person extraction sanity
    gemini_chunks    = len(gemini_resp)
    empty_gemini     = sum(1 for c in gemini_resp if not c.strip())

    # 5) Decide anomalies
    anomalies = {
        "empty_pages": empty_pages,
        "too_few_entities": total_entities < min_entities,
        "missing_needs_flag": not has_needs_flag,
        "empty_gemini_chunks": empty_gemini
    }

    # 6) Summarize metrics
    metrics = {
        "total_pages": total_pages,
        "total_entities": total_entities,
        "gemini_chunks": gemini_chunks,
        "passed_verification": passed_verif,
        "missing_fields_count": len(missing_fields),
        "needs_human_intervention": analysis.get("needs_human_intervention"),
        "anomalies": anomalies
    }

    # 7) Write metrics.json
    with open(out_metrics, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # 8) Print summary for CI/logs
    print("🔍 Data Quality Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    print("\n⚠️  Anomalies:", {k:v for k,v in anomalies.items() if v})

if __name__ == "__main__":
    main()
