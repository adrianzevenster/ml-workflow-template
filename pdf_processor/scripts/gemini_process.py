from google.cloud import aiplatform
from vertexai.language_models import TextGenerationModel
from config import PROJECT_ID, VTX_LOCATION, GEMINI_MODEL

def chunk_text(text: str, size: int = 1000, overlap: int = 200) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunks.append(" ".join(words[i : i + size]))
    return chunks

def extract_persons_from_text(text: str) -> list[str]:
    aiplatform.init(project=PROJECT_ID, location=VTX_LOCATION)
    model = TextGenerationModel.from_pretrained(GEMINI_MODEL)
    responses = []
    for chunk in chunk_text(text):
        prompt = f"Extract all PERSON names from the following text:\n\n{chunk}"
        resp = model.predict(prompt)
        responses.append(resp.text.strip())
    return responses
