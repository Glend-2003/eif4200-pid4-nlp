"""
sentiment.py — Análisis de Sentimiento en Español
Responsable: Jamel

Estrategia en capas (de mayor a menor capacidad, con degradación elegante):

  1. Modelo de HuggingFace (pysentimiento / RoBERTuito-es): comprende el
     contexto, las negaciones y el sarcasmo de forma nativa. Motor principal.
  2. Léxico de polaridad en español CON manejo de negación e intensificadores:
     fallback robusto que funciona sin conexión ni dependencias pesadas y que
     resuelve correctamente casos como "No es bueno" vs "Es bueno".
  3. Neutro por defecto si todo lo anterior falla.

Salida: tupla (etiqueta, score) con etiqueta en {'Positivo', 'Neutro', 'Negativo'}
y score en el rango [-1, 1] (negativo → polaridad negativa).
"""
import re
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Capa 1: Modelo de HuggingFace (carga perezosa, una sola vez por proceso)
# ---------------------------------------------------------------------------
_analyzer = None          # instancia cacheada del analizador
_hf_unavailable = False   # bandera para no reintentar si ya falló la carga

_HF_LABELS = {"POS": "Positivo", "NEU": "Neutro", "NEG": "Negativo"}


def _get_hf_analyzer():
    """
    Carga (una sola vez) el analizador de sentimiento de HuggingFace en español.

    Returns:
        El analizador de pysentimiento, o None si no está disponible.
    """
    global _analyzer, _hf_unavailable
    if _analyzer is not None:
        return _analyzer
    if _hf_unavailable:
        return None
    try:
        # Silenciar el ruido de descarga/carga de transformers para una consola limpia.
        import os
        os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
        os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
        try:
            from transformers.utils import logging as hf_logging
            hf_logging.set_verbosity_error()
        except Exception:
            pass

        from pysentimiento import create_analyzer
        _analyzer = create_analyzer(task="sentiment", lang="es")
        logger.info("Modelo de sentimiento HuggingFace (pysentimiento/es) cargado.")
        return _analyzer
    except Exception as e:
        # Sin red, sin la librería, o sin el modelo descargado: usamos el léxico.
        _hf_unavailable = True
        logger.warning(
            f"Modelo HuggingFace no disponible ({e}). Se usará el léxico en español."
        )
        return None


def _analyze_hf(text: str):
    """
    Clasifica con el modelo transformer de HuggingFace.

    Returns:
        Tupla (etiqueta, score) o None si el modelo no está disponible.
    """
    analyzer = _get_hf_analyzer()
    if analyzer is None:
        return None
    result = analyzer.predict(text)
    probas = getattr(result, "probas", {}) or {}
    label = _HF_LABELS.get(result.output, "Neutro")
    # Score firmado: confianza en positivo menos confianza en negativo.
    score = round(float(probas.get("POS", 0.0)) - float(probas.get("NEG", 0.0)), 4)
    return label, score


# ---------------------------------------------------------------------------
# Capa 2: Léxico en español con manejo de negación e intensificadores
# ---------------------------------------------------------------------------
_POSITIVOS = {
    "excelente", "increíble", "increible", "perfecto", "perfecta", "perfectas",
    "perfectos", "bueno", "buena", "buenos", "buenas", "encantó", "encanto",
    "maravilloso", "maravillosa", "fantástico", "fantastico", "feliz", "contento",
    "contenta", "recomiendo", "recomendado", "recomendable", "rápido", "rapido",
    "rápida", "rapida", "calidad", "aceptable", "bien", "cumple", "superó",
    "supero", "satisfecho", "satisfecha", "genial", "espectacular", "agradable",
    "cómodo", "comodo", "útil", "util", "eficiente", "impecable", "encanta",
    "mejor", "amable", "barato", "económico", "economico", "puntual",
}
_NEGATIVOS = {
    "pésimo", "pesimo", "terrible", "malo", "mala", "malos", "malas", "roto",
    "rota", "rotos", "peor", "horrible", "deficiente", "decepcionante",
    "decepción", "decepcion", "decepcionado", "error", "errores", "fallo",
    "falla", "fallas", "demora", "demoró", "demoro", "tardó", "tardo",
    "tardaron", "lástima", "lastima", "caro", "carísimo", "carisimo", "lento",
    "lenta", "incómodo", "incomodo", "inútil", "inutil", "estafa", "fraude",
    "sucio", "dañado", "danado", "defectuoso", "asco", "odio", "frustrante",
}
# Palabras que invierten la polaridad de los términos que les siguen.
_NEGADORES = {
    "no", "nunca", "jamás", "jamas", "tampoco", "ni", "sin", "nada", "nadie",
    "ningún", "ningun", "ninguna", "ninguno",
}
# Palabras que amplifican la intensidad del término que les sigue.
_INTENSIFICADORES = {
    "muy", "súper", "super", "demasiado", "tan", "bastante", "totalmente",
    "completamente", "extremadamente", "realmente", "absolutamente",
}

# Cuántas palabras hacia adelante alcanza el efecto de una negación.
_VENTANA_NEGACION = 3


def _analyze_lexicon(text: str) -> tuple:
    """
    Clasifica usando un léxico de polaridad en español con reglas de negación.

    Recorre el texto palabra por palabra. Una negación ("no", "nunca", ...)
    invierte la polaridad de los siguientes términos dentro de una ventana, y
    un intensificador ("muy", "súper", ...) amplifica el término que le sigue.
    Esto permite distinguir "No es bueno" (Negativo) de "Es bueno" (Positivo).

    Args:
        text: Texto original de la reseña (sin limpiar, para conservar el "no").

    Returns:
        Tupla (etiqueta, score normalizado en [-1, 1]).
    """
    tokens = re.findall(r"[a-záéíóúüñ]+", text.lower())
    score = 0.0
    hits = 0
    neg_window = 0   # palabras restantes bajo efecto de negación
    intens = 1.0     # multiplicador del próximo término con polaridad

    for tok in tokens:
        if tok in _NEGADORES:
            neg_window = _VENTANA_NEGACION
            continue
        if tok in _INTENSIFICADORES:
            intens = 1.5
            continue

        polarity = 1.0 if tok in _POSITIVOS else (-1.0 if tok in _NEGATIVOS else 0.0)

        if polarity != 0.0:
            if neg_window > 0:
                polarity = -polarity   # la negación invierte el sentido
            score += polarity * intens
            hits += 1
            intens = 1.0
            neg_window = 0
        elif neg_window > 0:
            neg_window -= 1            # la negación se va agotando

    if hits == 0:
        return "Neutro", 0.0

    # Promedio acotado a [-1, 1] para mantener un score interpretable.
    norm = max(-1.0, min(1.0, score / hits))
    return _label_from_score(norm), round(norm, 4)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
def analyze_sentiment(text: str) -> tuple:
    """
    Clasifica el sentimiento de un texto en español.

    Usa el modelo de HuggingFace si está disponible; si no, cae sobre el léxico
    con manejo de negación. Nunca lanza excepción: ante cualquier fallo devuelve
    ('Neutro', 0.0).

    Args:
        text: Texto de la reseña (original, no limpio).

    Returns:
        Tupla (etiqueta, score) con etiqueta en {'Positivo', 'Neutro', 'Negativo'}.
    """
    if not text or not isinstance(text, str):
        return "Neutro", 0.0

    # --- Capa 1: modelo de HuggingFace ---
    try:
        hf = _analyze_hf(text)
        if hf is not None:
            return hf
    except Exception as e:
        logger.warning(f"Fallo del modelo HuggingFace, se usa el léxico: {e}")

    # --- Capa 2: léxico en español con negación ---
    try:
        return _analyze_lexicon(text)
    except Exception as e:
        logger.error(f"Error en analyze_sentiment: {e}")
        return "Neutro", 0.0


def _label_from_score(score: float) -> str:
    """Convierte un score de polaridad en etiqueta de sentimiento."""
    if score > 0.1:
        return "Positivo"
    elif score < -0.1:
        return "Negativo"
    return "Neutro"
