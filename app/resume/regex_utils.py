import re
from typing import Dict, List

PII_PATTERNS = {
    "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:[a-zA-Z]{2,})\b",
    "phone": r"\b(?:\+?82[-.\s]?1[016789]|01[016789])[-.\s]?\d{3,4}[-.\s]?\d{4}\b",
    "ssn": r"\b\d{6}-[1-4]\d{6}\b",
    "url": r"\bhttps?://[^\s<>\[\](){}\"]+\b",
    "road_address" : r"\b(?:서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)\s[\w\d가-힣]{1,20}(로|길)\s\d{1,4}(?:-\d{1,4})?",
    "jibeon_address" : r"\b(?:서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)\s[\w\d가-힣]{1,20}(읍|면|동|가)?\s?\d{1,4}(?:-\d{1,4})?",
    "name": r"(이름[:：]?\s?[가-힣]{2,4})",
    "school": r"(?:[가-힣]+대학교|[가-힣]+고등학교|[가-힣]+중학교|[가-힣]+초등학교)",
    "birth": r"생년월일[^\d]{0,5}((?:19|20)\d{2}[./-](?:0[1-9]|1[0-2])[./-](?:0[1-9]|[12][0-9]|3[01]))",
    "card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "driver_license": r"\b\d{2}-\d{2}-\d{6}-\d{2}\b",
    "passport": r"\b[A-Z][0-9]{7,8}\b",
    "health_insurance": r"\b\d{6}[-]?\d{7}|\d{10,13}\b"
}

def detect_regex_pii(text: str) -> Dict[str, List[str]]:

    detected = {}
    for label, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            detected[label] = list(set(matches))  # 중복 제거
    return detected
