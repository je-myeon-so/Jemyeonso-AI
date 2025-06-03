from pathlib import Path

def load_prompt(filename: str) -> str:
    base_dir = Path(__file__).resolve().parent.parent  # app/interview → app
    prompt_path = base_dir / "prompts" / filename
    return prompt_path.read_text(encoding="utf-8")
