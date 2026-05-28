"""
tokenizer.py — Tokenización y Lematización con spaCy
Responsable: Dorian

Requiere: python -m spacy download es_core_news_lg
"""
import logging

logger = logging.getLogger(__name__)

try:
    import spacy
    nlp = spacy.load("es_core_news_lg")
    logger.info("Modelo spaCy cargado.")
except OSError:
    nlp = None
    logger.warning("Modelo no encontrado. Ejecuta: python -m spacy download es_core_news_lg")
except ImportError:
    nlp = None
    logger.warning("spaCy no instalado.")


def tokenize_and_lemmatize(text: str) -> list:
    if not text:
        return []
    if nlp is None:
        return text.split()
    try:
        doc = nlp(text)
        return [
            token.lemma_.lower()
            for token in doc
            if not token.is_punct and not token.is_space and len(token.lemma_) > 2
        ]
    except Exception as e:
        logger.error(f"Error en tokenize_and_lemmatize: {e}")
        return text.split()
