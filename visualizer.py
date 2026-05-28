"""
visualizer.py — WordCloud y gráficos de sentimiento
Responsable: Yeye
"""
import os
import logging
from collections import Counter

logger = logging.getLogger(__name__)
OUTPUT_DIR = "output"


def generate_wordcloud(results: list):
    try:
        from wordcloud import WordCloud
        import matplotlib.pyplot as plt

        all_text = " ".join([r["lemmatized"] for r in results if r["lemmatized"]])
        if not all_text.strip():
            logger.warning("No hay texto para WordCloud.")
            return

        wc = WordCloud(width=900, height=500, background_color="white",
                       colormap="Blues", max_words=80, collocations=False).generate(all_text)

        plt.figure(figsize=(12, 6))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title("Palabras más frecuentes en las reseñas", fontsize=16, pad=15)
        plt.tight_layout()
        path = os.path.join(OUTPUT_DIR, "wordcloud.png")
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info(f"WordCloud guardado en {path}")
    except Exception as e:
        logger.error(f"Error en WordCloud: {e}")


def generate_sentiment_chart(results: list):
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns

        counts = Counter([r["sentiment"] for r in results])
        labels = ["Positivo", "Neutro", "Negativo"]
        values = [counts.get(l, 0) for l in labels]
        colors = ["#4CAF50", "#FFC107", "#F44336"]

        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=1.2)

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(val), ha="center", va="bottom", fontsize=13, fontweight="bold")

        ax.set_title("Distribución de Sentimientos", fontsize=15, pad=12)
        ax.set_xlabel("Sentimiento", fontsize=12)
        ax.set_ylabel("Cantidad de reseñas", fontsize=12)
        ax.set_ylim(0, max(values) + 2)
        plt.tight_layout()
        path = os.path.join(OUTPUT_DIR, "sentiment_chart.png")
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info(f"Gráfico guardado en {path}")
    except Exception as e:
        logger.error(f"Error en gráfico: {e}")


def print_comparison_table(results: list):
    print(f"\n{'─'*90}")
    print(f"{'#':<4} {'ORIGINAL':<35} {'LEMATIZADO':<30} {'SENTIMIENTO':<12} {'SCORE'}")
    print(f"{'─'*90}")
    for i, r in enumerate(results, 1):
        orig = r["original"][:33] + ".." if len(r["original"]) > 35 else r["original"]
        lem = r["lemmatized"][:28] + ".." if len(r["lemmatized"]) > 30 else r["lemmatized"]
        print(f"{i:<4} {orig:<35} {lem:<30} {r['sentiment']:<12} {r['score']}")
    print(f"{'─'*90}\n")
