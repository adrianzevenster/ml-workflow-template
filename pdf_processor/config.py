import os

# Database
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# GCS
GCS_BUCKET = os.getenv("GCS_BUCKET")

# Document AI
PROJECT_ID      = os.getenv("GCP_PROJECT")
DOCAI_LOCATION  = os.getenv("DOCAI_LOCATION", "us")
DOCAI_PROCESSOR = os.getenv("DOCAI_PROCESSOR_ID")

# Vertex AI / Gemini
VTX_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "text-bison@001")
