import re
from typing import Dict, List

PII_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"01[016789]-?\d{3,4}-?\d{4}",
    "ssn": r"\d{6}-[1-4]\d{6}",
    "url": r"https?://[^\s]+"
}

def detect_regex_pii(text: str) -> Dict[str, List[str]]:
    detected = {}
    for label, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            detected[label] = matches
    return detected
