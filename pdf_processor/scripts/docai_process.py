from google.cloud import documentai_v1 as documentai
from config import PROJECT_ID, DOCAI_LOCATION, DOCAI_PROCESSOR

def process_with_document_ai(pdf_bytes: bytes) -> documentai.Document:
    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(PROJECT_ID, DOCAI_LOCATION, DOCAI_PROCESSOR)
    raw = documentai.RawDocument(content=pdf_bytes, mime_type="application/pdf")
    req = documentai.ProcessRequest(name=name, raw_document=raw)
    res = client.process_document(request=req)
    return res.document
