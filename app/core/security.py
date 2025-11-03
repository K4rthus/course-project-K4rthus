import os
import uuid
from pathlib import Path
from typing import Tuple

MAX_FILE_SIZE = 5_000_000
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "application/pdf"}

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8"
PDF_SIGNATURE = b"%PDF"

def sniff_file_type(data: bytes) -> str:
    """Определяем тип файла по magic bytes"""
    if data.startswith(PNG_SIGNATURE):
        return "image/png"
    elif data.startswith(JPEG_SIGNATURE):
        return "image/jpeg"
    elif data.startswith(PDF_SIGNATURE):
        return "application/pdf"
    else:
        return "unknown"

def validate_and_save_file(
    upload_dir: str,
    filename: str,
    data: bytes
) -> Tuple[bool, str]:
    """Безопасная валидация и сохранение файла"""
    
    if len(data) > MAX_FILE_SIZE:
        return False, "file_too_large"
    
    detected_type = sniff_file_type(data)
    if detected_type == "unknown" or detected_type not in ALLOWED_MIME_TYPES:
        return False, "invalid_file_type"
    
    if ".." in filename or "/" in filename or "\\" in filename:
        return False, "path_traversal_attempt"
    
    root = Path(upload_dir).resolve(strict=True)
    
    file_ext = {
        "image/png": ".png",
        "image/jpeg": ".jpg", 
        "application/pdf": ".pdf"
    }[detected_type]
    
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = (root / safe_filename).resolve()
    
    if not str(file_path).startswith(str(root)):
        return False, "path_traversal_attempt"
    
    try:
        with open(file_path, "wb") as f:
            f.write(data)
        return True, safe_filename
    except IOError:
        return False, "save_failed"

def sanitize_text(text: str, max_length: int = 2000) -> str:
    """Санитизация пользовательского текста"""
    if len(text) > max_length:
        text = text[:max_length]
    
    text = (
        text.replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
    )
    
    return text

def setup_rate_limiting(app):
    """
    Setup rate limiting middleware for the application.
    """
    print("Rate limiting setup - stub implementation")