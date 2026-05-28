"""
main.py — Orquestación del pipeline completo de análisis de sentimiento PLN.
Responsable: Glend

Uso:
    python main.py --input data/sample_reviews.csv
"""
import argparse
import logging
import os
import sys

from data_loader import load_data
from cleaner import clean_text
from tokenizer import tokenize_and_lemmatize
from sentiment import analyze_sentiment
from visualizer import generate_wordcloud, generate_sentiment_chart, print_comparison_table

# Configuración del logger del módulo principal
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline(input_path: str) -> None:
    """
    Ejecuta el pipeline completo de PLN sobre el archivo indicado.

    Etapas:
        1. Carga de datos (data_loader)
        2. Limpieza de texto (cleaner)
        3. Tokenización y lematización (tokenizer)
        4. Análisis de sentimiento (sentiment)
        5. Visualización y tabla comparativa (visualizer)

    Los resultados se guardan en la carpeta output/.

    Args:
        input_path: Ruta al archivo de entrada (CSV, Excel o TXT).
    """
    # Encabezado del pipeline
    print(f"\n{'='*55}")
    print(" PIPELINE DE ANÁLISIS DE SENTIMIENTO — PLN")
    print(f"{'='*55}")
    print(f" Archivo: {input_path}\n")

    # --- Etapa 1: Carga de datos ---
    try:
        reviews = load_data(input_path)
    except Exception as e:
        logger.error(f"Fallo crítico al cargar datos: {e}")
        return

    if not reviews:
        logger.error("No se pudieron cargar datos. Verifique el archivo de entrada.")
        return

    print(f" {len(reviews)} comentarios cargados.\n")

    # --- Etapas 2-4: Procesamiento de cada reseña ---
    results = []
    for i, review in enumerate(reviews, 1):
        original = review.strip()
        if not original:
            # Ignorar líneas vacías
            continue

        try:
            cleaned = clean_text(original)
        except Exception as e:
            logger.warning(f"[Reseña {i}] Error en limpieza: {e}. Se usará el texto original.")
            cleaned = original

        try:
            tokens = tokenize_and_lemmatize(cleaned)
            lemmatized_text = " ".join(tokens)
        except Exception as e:
            logger.warning(f"[Reseña {i}] Error en lematización: {e}. Se usará el texto limpio.")
            lemmatized_text = cleaned

        try:
            sentiment, score = analyze_sentiment(original)
        except Exception as e:
            logger.warning(f"[Reseña {i}] Error en análisis de sentimiento: {e}. Se asignará 'Neutro'.")
            sentiment, score = "Neutro", 0.0

        results.append({
            "original": original,
            "cleaned": cleaned,
            "lemmatized": lemmatized_text,
            "sentiment": sentiment,
            "score": score,
        })

    if not results:
        logger.error("No se generaron resultados. Verifique que el archivo tenga contenido válido.")
        return

    # --- Etapa 5: Visualización ---
    # Crear el directorio de salida si no existe
    try:
        os.makedirs("output", exist_ok=True)
    except OSError as e:
        logger.error(f"No se pudo crear la carpeta 'output/': {e}")
        return

    try:
        print_comparison_table(results)
    except Exception as e:
        logger.error(f"Error al imprimir la tabla comparativa: {e}")

    try:
        generate_wordcloud(results)
    except Exception as e:
        logger.error(f"Error al generar el WordCloud: {e}")

    try:
        generate_sentiment_chart(results)
    except Exception as e:
        logger.error(f"Error al generar el gráfico de sentimientos: {e}")

    print("\n Proceso completado. Revisa la carpeta output/")
    print(f"{'='*55}\n")


def _parse_args() -> argparse.Namespace:
    """
    Configura y parsea los argumentos de línea de comandos.

    Returns:
        Namespace con los argumentos parseados.
    """
    parser = argparse.ArgumentParser(
        description="Pipeline de Análisis de Sentimiento con PLN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Ejemplo:\n  python main.py --input data/sample_reviews.csv",
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="ARCHIVO",
        help="Ruta al archivo de entrada (CSV, Excel .xlsx/.xls, o TXT)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    # Validar existencia del archivo antes de iniciar el pipeline
    if not os.path.exists(args.input):
        logger.error(f"Archivo no encontrado: '{args.input}'")
        sys.exit(1)

    if not os.path.isfile(args.input):
        logger.error(f"La ruta indicada no es un archivo: '{args.input}'")
        sys.exit(1)

    run_pipeline(args.input)
