"""
modules/pdf_extractor.py
========================
Handles all PDF reading and text extraction.
Uses PyPDF2 to pull plain text from each page of an uploaded file.
"""

import io
import PyPDF2


def extract_text(pdf_file) -> str:
    """
    Extract plain text from a Streamlit UploadedFile (PDF).

    Args:
        pdf_file: A Streamlit UploadedFile object (file-like, .read()-able).

    Returns:
        A single string of all text across every page.
        Returns "" if the file is empty, unreadable, or not a valid PDF.
    """
    try:
        # Read raw bytes — works whether the file pointer is fresh or reset
        raw_bytes = pdf_file.read()

        if not raw_bytes:
            return ""

        reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))

        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text.strip())

        return " ".join(pages_text).strip()

    except PyPDF2.errors.PdfReadError:
        # Corrupted or password-protected PDF
        return ""
    except Exception:
        # Catch-all: don't crash the whole app for one bad file
        return ""


def clean_candidate_name(filename: str) -> str:
    """
    Derive a human-readable candidate name from the PDF filename.

    Example:
        "john_doe_resume.pdf"  →  "John Doe Resume"
        "Jane-Smith-CV.pdf"    →  "Jane Smith Cv"

    Args:
        filename: Raw filename string (with or without .pdf extension).

    Returns:
        A title-cased string suitable for display.
    """
    name = filename.replace(".pdf", "")
    name = name.replace("_", " ").replace("-", " ")
    return name.title()