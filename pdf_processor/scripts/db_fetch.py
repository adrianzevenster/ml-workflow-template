import mysql.connector
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME

def fetch_pdf_from_db(record_id: int) -> bytes:
    conn = mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
    )
    cursor = conn.cursor()
    cursor.execute("SELECT pdf_blob FROM documents WHERE id = %s", (record_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"No record found for id={record_id}")
    return row[0]
