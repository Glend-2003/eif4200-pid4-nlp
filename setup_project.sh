#!/bin/bash
# Ejecutar desde dentro de ~/Documentos/GitHub/eif4200-pid4-nlp

echo "Creando estructura del proyecto..."

# ── .gitignore ──
cat > .gitignore << 'EOF'
venv/
__pycache__/
*.pyc
*.pyo
.env
output/
*.png
*.jpg
.DS_Store
Thumbs.db
EOF

# ── requirements.txt ──
cat > requirements.txt << 'EOF'
spacy==3.7.4
textblob==0.18.0
vaderSentiment==3.3.2
matplotlib==3.8.4
seaborn==0.13.2
wordcloud==1.9.3
pandas==2.2.2
openpyxl==3.1.2
EOF

# ── README.md ──
cat > README.md << 'EOF'
# EIF-4200 — PID IV: Sistema de Análisis de Sentimiento con PLN

**Curso:** EIF-4200 Inteligencia Artificial I — Semestre 2026
**Profesor:** Lic. Adán Carranza Alfaro
**Entrega:** 06 de junio del 2026

## Equipo

| Integrante | Módulo |
|---|---|
| Glend | `main.py` + `data_loader.py` |
| Carranza | `cleaner.py` |
| Dorian | `tokenizer.py` |
| Jamel | `sentiment.py` |
| Yeye | `visualizer.py` |

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download es_core_news_lg
```

## Uso

```bash
python main.py --input data/sample_reviews.csv
```
EOF

# ── data/ ──
mkdir -p data output

cat > data/sample_reviews.csv << 'EOF'
id,review
1,"El producto llegó en perfectas condiciones, muy buena calidad"
2,"Pésimo servicio, el paquete llegó roto y no me han respondido"
3,"Está bien, cumple con lo que promete"
4,"Excelente compra, lo recomiendo totalmente"
5,"No es bueno, esperaba algo mejor por ese precio"
6,"Regular, ni muy bueno ni muy malo"
7,"Me encantó, llegó antes de lo esperado"
8,"Terrible experiencia, jamás volvería a comprar aquí"
9,"Producto aceptable, la entrega fue rápida"
10,"Increíble calidad, superó mis expectativas"
EOF

# ── main.py ──
cat > main.py << 'EOF'
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
EOF

# ── data_loader.py ──
cat > data_loader.py << 'EOF'
"""
data_loader.py — Carga de archivos CSV, Excel y TXT
Responsable: Glend
"""
import os
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_data(filepath: str) -> list:
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".csv":
            return _load_csv(filepath)
        elif ext in (".xlsx", ".xls"):
            return _load_excel(filepath)
        elif ext == ".txt":
            return _load_txt(filepath)
        else:
            logger.error(f"Formato no soportado: {ext}")
            return []
    except Exception as e:
        logger.error(f"Error al cargar archivo: {e}")
        return []


def _load_csv(filepath):
    import pandas as pd
    df = pd.read_csv(filepath)
    col = _find_text_column(df)
    logger.info(f"CSV cargado — columna '{col}', {len(df)} filas.")
    return df[col].dropna().astype(str).tolist()


def _load_excel(filepath):
    import pandas as pd
    df = pd.read_excel(filepath)
    col = _find_text_column(df)
    logger.info(f"Excel cargado — columna '{col}', {len(df)} filas.")
    return df[col].dropna().astype(str).tolist()


def _load_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    logger.info(f"TXT cargado — {len(lines)} líneas.")
    return lines


def _find_text_column(df):
    candidates = ["review", "comment", "text", "comentario", "reseña"]
    for col in df.columns:
        if col.lower() in candidates:
            return col
    for col in df.columns:
        if df[col].dtype == object:
            return col
    return df.columns[0]
EOF

# ── cleaner.py ──
cat > cleaner.py << 'EOF'
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
EOF

# ── tokenizer.py ──
cat > tokenizer.py << 'EOF'
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
EOF

# ── sentiment.py ──
cat > sentiment.py << 'EOF'
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
EOF

# ── visualizer.py ──
cat > visualizer.py << 'EOF'
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
EOF

echo ""
echo "✅ Todos los archivos creados."
echo ""
echo "Ahora ejecuta:"
echo "  git add ."
echo "  git commit -m 'feat: estructura inicial del proyecto PLN'"
echo "  git push origin main"
