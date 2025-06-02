import re
from typing import Dict, List

PII_PATTERNS = {
    "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:[a-zA-Z]{2,})\b",
    "phone": r"\b(?:\+?82[-.\s]?1[016789]|01[016789])[-.\s]?\d{3,4}[-.\s]?\d{4}\b",
    "ssn": r"\b\d{6}-[1-4]\d{6}\b",
    "url": r"\bhttps?://[^\s<>\[\](){}\"]+\b",
    "address": r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[^\n]{1,50}",
    "name": r"(이름[:：]?\s?[가-힣]{2,4})"

}

def detect_regex_pii(text: str) -> Dict[str, List[str]]:

    detected = {}
    for label, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            detected[label] = list(set(matches))  # 중복 제거
    return detected
