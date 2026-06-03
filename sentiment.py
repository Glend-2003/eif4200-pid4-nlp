"""
sentiment.py — Análisis de Sentimiento en Español
Responsable: Jamel

Estrategia principal: TextBlob con traducción al inglés vía TextBlob.translate()
Fallback 1:           Léxico de polaridad propio en español
Fallback 2:           Retorna Neutro con score 0.0
"""
import logging

logger = logging.getLogger(__name__)

# Léxico de polaridad en español para el fallback sin traducción
_POSITIVOS = {
    "excelente", "increíble", "perfecto", "bueno", "buena", "encantó", "maravilloso",
    "fantástico", "feliz", "contento", "recomiendo", "rápido", "rápida", "calidad",
    "aceptable", "bien", "cumple", "antes", "superó", "expectativas", "satisfecho",
}
_NEGATIVOS = {
    "pésimo", "terrible", "malo", "mala", "roto", "rota", "respondido", "jamás",
    "volvería", "peor", "horrible", "deficiente", "decepcionante", "nunca", "error",
    "fallo", "demora", "tardó", "tardaron", "lastima", "lástima",
}


def analyze_sentiment(text: str) -> tuple:
    """
    Clasifica el sentimiento de un texto en español.

    Intenta traducir a inglés y usar TextBlob; si la traducción no está disponible
    cae sobre el léxico propio en español.

    Args:
        text: Texto de la reseña (original, no limpio).

    Returns:
        Tupla (etiqueta: str, score: float) donde etiqueta es
        'Positivo', 'Neutro' o 'Negativo'.
    """
    if not text or not isinstance(text, str):
        return "Neutro", 0.0

    # --- Intento principal: TextBlob con traducción ---
    try:
        from textblob import TextBlob
        translated = TextBlob(text).translate(from_lang="es", to="en")
        score = translated.sentiment.polarity
        label = _label_from_score(score)
        return label, round(score, 4)
    except Exception:
        # La API de traducción de TextBlob puede fallar en entornos sin acceso a red
        pass

    # --- Fallback: léxico propio en español ---
    try:
        return _analyze_lexicon(text)
    except Exception as e:
        logger.error(f"Error en analyze_sentiment: {e}")
        return "Neutro", 0.0


# def _analyze_vader(text: str) -> tuple:
#     """
#     Alternativa usando vaderSentiment (para inglés).
#     Requiere traducción previa al inglés.
#     """
#     from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#     analyzer = SentimentIntensityAnalyzer()
#     scores = analyzer.polarity_scores(text)
#     compound = scores["compound"]
#     if compound >= 0.05:
#         return "Positivo", compound
#     elif compound <= -0.05:
#         return "Negativo", compound
#     return "Neutro", compound


def _analyze_lexicon(text: str) -> tuple:
    """
    Clasifica usando un léxico simple de palabras positivas/negativas en español.

    Args:
        text: Texto en español.

    Returns:
        Tupla (etiqueta, score aproximado).
    """
    tokens = set(text.lower().split())
    pos = len(tokens & _POSITIVOS)
    neg = len(tokens & _NEGATIVOS)

    if pos == 0 and neg == 0:
        return "Neutro", 0.0

    # Score normalizado en [-1, 1]
    total = pos + neg
    score = (pos - neg) / total
    return _label_from_score(score), round(score, 4)


def _label_from_score(score: float) -> str:
    """Convierte un score de polaridad en etiqueta de sentimiento."""
    if score > 0.1:
        return "Positivo"
    elif score < -0.1:
        return "Negativo"
    return "Neutro"
