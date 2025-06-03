from transformers import pipeline
from app.core.regex_utils import detect_regex_pii
from typing import Dict

# 사람이 읽기 쉬운 라벨 매핑
NER_LABEL_MAP = {
    "PER": "name",
    "LOC": "location",
    "ORG": "organization",
    "MISC": "misc"
}

# NER 파이프라인 초기화
ner = pipeline("ner", model="FacebookAI/xlm-roberta-large-finetuned-conll03-english", aggregation_strategy="simple")

def detect_pii(text: str, debug: bool = False) -> Dict:
    ner_entities = ner(text)
    regex_result = detect_regex_pii(text)

    ner_result = {}
    for ent in ner_entities:
        raw_label = ent["entity_group"].upper()
        mapped_label = NER_LABEL_MAP.get(raw_label)
        if mapped_label in ["name", "location"]:  # 원하는 항목만 포함
            ner_result.setdefault(mapped_label, []).append(ent["word"])

    if debug:
        print("\n📌 [NER 결과]")
        for label, items in ner_result.items():
            print(f"- {label}: {list(set(items))}")

        print("\n📌 [Regex 결과]")
        for label, items in regex_result.items():
            print(f"- {label}: {list(set(items))}")

    masked_text = text

    # Regex 기반 마스킹
    for label, matches in regex_result.items():
        for match in set(matches):
            match_str = "".join(match) if isinstance(match, tuple) else match
            masked_text = masked_text.replace(match_str, f"[REDACTED_{label.upper()}]")

    # NER 기반 마스킹
    for label, words in ner_result.items():
        for word in sorted(set(words), key=len, reverse=True):
            masked_text = masked_text.replace(word, f"[REDACTED_{label.upper()}]")

    # 최종적으로 감지된 PII 종류 (NER + Regex 통합)
    detected_labels = set(regex_result.keys()) | set(ner_result.keys())

    return {
        "regex_result": regex_result,
        "ner_result": ner_result,
        "anonymized_text": masked_text,
        "detected_pii_fields": list(detected_labels),
        "deleted_fields": list(detected_labels)
    }

# 테스트용
if __name__ == "__main__":
    raw_text = """
    성 명 이수민 영 문 Lee sumin
    연 락 처 010-0000-0000 생년월일 2001.01.01
    학력사항: 2017-2019 광남고등학교 졸업, 2020-2024 한양대학교 컴퓨터공학과 졸업
    성적: 3.8/4.5
    자격증: 정보처리기사 (2023.02.20), 빅데이터분석기사 (2021.10.01)
    활동: 2022.10.28 교내 해커톤 은상, 2023.12.12 네이버 AI 해커톤 본선 진출
    """

    result = detect_pii(raw_text, debug=True)

    print("\n🔒 [최종 마스킹 텍스트]")
    print(result["anonymized_text"])