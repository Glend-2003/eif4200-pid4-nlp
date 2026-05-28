"""
main.py — Integración del pipeline completo de PLN
Responsable: Glend
"""
import argparse
import os
from data_loader import load_data
from cleaner import clean_text
from tokenizer import tokenize_and_lemmatize
from sentiment import analyze_sentiment
from visualizer import generate_wordcloud, generate_sentiment_chart, print_comparison_table


def run_pipeline(input_path: str):
    print(f"\n{'='*55}")
    print(" PIPELINE DE ANÁLISIS DE SENTIMIENTO — PLN")
    print(f"{'='*55}")
    print(f" Archivo: {input_path}\n")

    reviews = load_data(input_path)
    if not reviews:
        print("[ERROR] No se pudieron cargar datos.")
        return

    print(f" {len(reviews)} comentarios cargados.\n")
    results = []

    for review in reviews:
        original = review.strip()
        if not original:
            continue
        cleaned = clean_text(original)
        lemmatized_tokens = tokenize_and_lemmatize(cleaned)
        lemmatized_text = " ".join(lemmatized_tokens)
        sentiment, score = analyze_sentiment(original)
        results.append({
            "original": original,
            "cleaned": cleaned,
            "lemmatized": lemmatized_text,
            "sentiment": sentiment,
            "score": score
        })

    os.makedirs("output", exist_ok=True)
    print_comparison_table(results)
    generate_wordcloud(results)
    generate_sentiment_chart(results)
    print("\n Proceso completado. Revisa la carpeta output/")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análisis de Sentimiento con PLN")
    parser.add_argument("--input", required=True, help="Ruta al archivo CSV, Excel o TXT")
    args = parser.parse_args()
    if not os.path.exists(args.input):
        print(f"[ERROR] Archivo no encontrado: {args.input}")
    else:
        run_pipeline(args.input)
