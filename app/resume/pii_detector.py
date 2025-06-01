from transformers import pipeline
from app.resume.regex_utils import detect_regex_pii
from typing import Dict, List

ner = pipeline("ner", model="FacebookAI/xlm-roberta-large-finetuned-conll03-english", aggregation_strategy="simple")

def detect_pii(text: str) -> Dict:
    ner_entities = ner(text)
    regex_entities = detect_regex_pii(text)

    masked_text = text
    detected_fields = set()
    deleted_fields = []

    for ent in ner_entities:
        label = ent["entity_group"].lower()
        if label in ["person", "organization", "location"]:
            masked_text = masked_text.replace(ent["word"], f"[REDACTED_{label.upper()}]")
            detected_fields.add(label)
            deleted_fields.append(label)

    for label, matches in regex_entities.items():
        for match in matches:
            masked_text = masked_text.replace(match, f"[REDACTED_{label.upper()}]")
        detected_fields.add(label)
        deleted_fields.append(label)

    return {
        "anonymized_text": masked_text,
        "detected_pii_fields": list(detected_fields),
        "deleted_fields": list(set(deleted_fields)),
    }
