"""
cleaner.py — Limpieza de texto y eliminación de stop words
Responsable: Carranza
"""
import re
import logging

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    "de", "del", "al", "a", "en", "con", "por", "para",
    "que", "y", "o", "pero", "si", "no", "se", "su", "sus",
    "me", "te", "le", "nos", "les", "lo", "es", "son", "fue",
    "era", "este", "esta", "estos", "estas", "muy", "más",
    "como", "hay", "ya", "mi", "mis", "tu", "tus"
}


def clean_text(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    try:
        text = text.lower()
        text = re.sub(r"http\S+|www\S+", "", text)
        text = re.sub(r"[^a-záéíóúüñ\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        tokens = [t for t in text.split() if t not in STOP_WORDS]
        return " ".join(tokens)
    except Exception as e:
        logger.error(f"Error en clean_text: {e}")
        return text
