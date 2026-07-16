# app/core/validators.py
"""
Custom validators — malicious input detect karo aur reject karo.
"""

import re
from typing import Optional

# SQL injection patterns
SQL_INJECTION_PATTERNS = [
    r"(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|\bCREATE\b)",
    r"(--|;|\/\*|\*\/)",
    r"(\bOR\b\s+\d+\s*=\s*\d+)",
    r"(\bUNION\b\s+\bSELECT\b)",
    r"(xp_cmdshell|exec\s*\(|execute\s*\()",
]

# XSS patterns
XSS_PATTERNS = [
    r"<script[^>]*>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<img[^>]*onerror",
]

def check_sql_injection(value: str) -> bool:
    """True agar SQL injection pattern mile."""
    if not value:
        return False
    value_upper = value.upper()
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value_upper, re.IGNORECASE):
            return True
    return False

def check_xss(value: str) -> bool:
    """True agar XSS pattern mile."""
    if not value:
        return False
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False

def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    String ko sanitize karo:
    1. Trim karo
    2. Max length enforce karo
    3. Dangerous characters encode karo
    """
    if not value:
        return value

    # Trim
    value = value.strip()

    # Max length
    value = value[:max_length]

    # HTML entities encode karo
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    value = value.replace('"', "&quot;")
    value = value.replace("'", "&#x27;")

    return value

def validate_amount(amount: float) -> Optional[str]:
    """Amount validation."""
    if amount <= 0:
        return "Amount must be positive"
    if amount > 10_000_000:  # 1 crore limit
        return "Amount too large (max ₹1 crore)"
    return None

def validate_search_query(query: str) -> Optional[str]:
    """Search query validation."""
    if not query:
        return None
    if len(query) > 100:
        return "Search query too long (max 100 chars)"
    if check_sql_injection(query):
        return "Invalid search query"
    if check_xss(query):
        return "Invalid characters in search query"
    return None