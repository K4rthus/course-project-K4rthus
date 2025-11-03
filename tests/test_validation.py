import pytest
import os
from pathlib import Path
from app.core.security import validate_and_save_file, sanitize_text


def test_file_size_validation(tmp_path):
    """Тест на отклонение слишком больших файлов"""
    large_file = b"X" * (5_000_001)
    
    success, reason = validate_and_save_file(
        str(tmp_path), "test.png", large_file
    )
    
    assert not success
    assert reason == "file_too_large"


def test_magic_bytes_validation(tmp_path):
    """Тест на проверку magic bytes"""
    fake_png = b"FAKE_PNG_DATA" + b"0" * 100
    
    success, reason = validate_and_save_file(
        str(tmp_path), "test.png", fake_png
    )
    
    assert not success
    assert reason == "invalid_file_type"


def test_path_traversal_prevention(tmp_path):
    """Тест на защиту от path traversal"""
    traversal_filename = "../../etc/passwd"
    png_data = b"\x89PNG\r\n\x1a\n" + b"valid_png_data"
    
    success, reason = validate_and_save_file(
        str(tmp_path), traversal_filename, png_data
    )
    
    assert not success
    assert "traversal" in reason


def test_xss_sanitization():
    """Тест на санитизацию XSS"""
    malicious_text = '<script>alert("XSS")</script>'
    sanitized = sanitize_text(malicious_text)
    
    assert "<script>" not in sanitized
    assert "&lt;script&gt;" in sanitized


def test_text_length_limitation():
    """Тест на ограничение длины текста"""
    long_text = "A" * 3000
    sanitized = sanitize_text(long_text, max_length=2000)
    
    assert len(sanitized) == 2000