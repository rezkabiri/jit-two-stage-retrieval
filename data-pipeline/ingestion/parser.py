# data-pipeline/ingestion/parser.py
import os
import io
import logging
from pypdf import PdfReader
from typing import Dict, Any

logger = logging.getLogger(__name__)

def extract_text(file_content: bytes, file_name: str) -> str:
    """
    Extracts text from various file formats.
    """
    if file_name.lower().endswith(".pdf"):
        logger.info(f"📄 Extracting text from PDF: {file_name}")
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        logger.info(f"✅ Extracted {len(reader.pages)} pages from {file_name}")
        return text
    elif file_name.lower().endswith((".txt", ".md")):
        logger.info(f"📝 Extracting text from {file_name}")
        return file_content.decode("utf-8")
    else:
        logger.warning(f"⚠️ Unsupported file type for text extraction: {file_name}")
        return ""

def map_rbac_roles(file_path: str) -> Dict[str, Any]:
    """
    Maps the GCS folder path to RBAC roles based on naming conventions.
    Example: 'finance/reports/2024.pdf' -> role: 'finance'
    """
    logger.info(f"🏷️ Mapping RBAC roles for path: {file_path}")
    path_parts = file_path.split("/")
    
    # ... (role assignment logic)
    # ...
    # Map common folder patterns
    if "finance" in path_parts:
        role = "finance"
    elif "legal" in path_parts:
        role = "legal"
    elif "hr" in path_parts:
        role = "hr"
    elif "private" in path_parts:
        role = "internal"

    result = {
        "role": role,
        "folder": path_parts[0] if len(path_parts) > 1 else "root",
        "source_path": f"gs://{file_path}"
    }
    logger.info(f"✅ Assigned role '{role}' based on folder '{result['folder']}'")
    return result
