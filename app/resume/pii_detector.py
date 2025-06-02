from transformers import pipeline
from app.resume.regex_utils import detect_regex_pii
from typing import Dict, List

# NER 파이프라인 (기존 모델 유지)
ner = pipeline("ner", model="FacebookAI/xlm-roberta-large-finetuned-conll03-english", aggregation_strategy="simple")

def detect_pii(text: str) -> Dict:
    # 1. 탐지 수행
    ner_entities = ner(text)
    regex_result = detect_regex_pii(text)

    # 2. NER 결과 정리
    ner_result = {}
    for ent in ner_entities:
        label = ent["entity_group"].lower()
        if label in ["person", "organization", "location"]:
            ner_result.setdefault(label, []).append(ent["word"])

    # 3. 마스킹
    masked_text = text
    for label, words in ner_result.items():
        for word in set(words):
            masked_text = masked_text.replace(word, f"[REDACTED_{label.upper()}]")

    for label, matches in regex_result.items():
        for match in set(matches):
            masked_text = masked_text.replace(match, f"[REDACTED_{label.upper()}]")

    # 4. 반환 구조 (로그 작성용 포맷 포함)
    return {
        "regex_result": regex_result,
        "ner_result": ner_result,
        "anonymized_text": masked_text
    }