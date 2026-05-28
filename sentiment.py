"""
sentiment.py — Análisis de Sentimiento
Responsable: Jamel
"""
import logging

logger = logging.getLogger(__name__)


def analyze_sentiment(text: str) -> tuple:
    if not text or not isinstance(text, str):
        return "Neutro", 0.0
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        score = blob.sentiment.polarity
        if score > 0.1:
            label = "Positivo"
        elif score < -0.1:
            label = "Negativo"
        else:
            label = "Neutro"
        return label, round(score, 4)
    except Exception as e:
        logger.error(f"Error en analyze_sentiment: {e}")
        return "Neutro", 0.0
