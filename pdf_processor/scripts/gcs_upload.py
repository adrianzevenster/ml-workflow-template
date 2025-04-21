from google.cloud import storage
from config import GCS_BUCKET

def upload_to_gcs(dest_path: str, pdf_bytes: bytes) -> str:
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob   = bucket.blob(dest_path)
    blob.upload_from_string(pdf_bytes, content_type="application/pdf")
    return f"gs://{GCS_BUCKET}/{dest_path}"
