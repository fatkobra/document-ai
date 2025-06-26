import pdfplumber
from fastapi import UploadFile

def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extracts text from a PDF file using pdfplumber.

    Args:
        file (UploadFile): The uploaded PDF file from FastAPI.

    Returns:
        str: Extracted plain text content.
    """
    text = ""
    try:
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        text = f"Error reading PDF: {e}"
    return text.strip()