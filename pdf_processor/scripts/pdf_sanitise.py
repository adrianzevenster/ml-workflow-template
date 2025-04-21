import io
from PyPDF2 import PdfReader, PdfWriter

def split_pdf_pages(pdf_bytes: bytes) -> list[bytes]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    for page in reader.pages:
        writer = PdfWriter()
        writer.add_page(page)
        buf = io.BytesIO()
        writer.write(buf)
        pages.append(buf.getvalue())
    return pages
