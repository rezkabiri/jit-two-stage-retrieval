# data-pipeline/ingestion/parser.py
import os
import io
from pypdf import PdfReader
from typing import Dict, Any

def extract_text(file_content: bytes, file_name: str) -> str:
    """
    Extracts text from various file formats.
    """
    if file_name.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "
"
        return text
    elif file_name.lower().endswith((".txt", ".md")):
        return file_content.decode("utf-8")
    else:
        return ""

def map_rbac_roles(file_path: str) -> Dict[str, Any]:
    """
    Maps the GCS folder path to RBAC roles based on naming conventions.
    Example: 'finance/reports/2024.pdf' -> role: 'finance'
    """
    path_parts = file_path.split("/")
    
    # Default role
    role = "public"
    
    # Map common folder patterns
    if "finance" in path_parts:
        role = "finance"
    elif "legal" in path_parts:
        role = "legal"
    elif "hr" in path_parts:
        role = "hr"
    elif "private" in path_parts:
        role = "internal"

    return {
        "role": role,
        "folder": path_parts[0] if len(path_parts) > 1 else "root",
        "source_path": f"gs://{file_path}"
    }
