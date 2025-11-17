import re

def clean_text(text: str) -> str:
    """
    Lowercase, remove punctuation, normalize whitespace.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
