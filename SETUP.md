# Guía de Instalación y Ejecución

## Requisitos previos

- Python 3.10 o superior
- Git
- Conexión a internet (para descargar el modelo de spaCy)

---

## 1. Clonar el repositorio

```bash
git clone git@github.com:Glend-2003/eif4200-pid4-nlp.git
cd eif4200-pid4-nlp
```

---

## 2. Crear el entorno virtual

**Linux / Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

> Si en Linux sale error con `python3 -m venv`, ejecuta primero:
> ```bash
> sudo apt install python3.12-venv -y
> ```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Instalar el modelo de spaCy en español

```bash
pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.7.0/es_core_news_lg-3.7.0-py3-none-any.whl
```

> ⚠️ No uses `python -m spacy download es_core_news_lg` — puede fallar. Usa el comando de arriba.

---

## 5. Ejecutar el programa

```bash
python main.py --input data/sample_reviews.csv
```

También puedes usar tu propio archivo:

```bash
# Con archivo TXT (un comentario por línea)
python main.py --input data/mis_reviews.txt

# Con archivo Excel
python main.py --input data/mis_reviews.xlsx
```

---

## 6. Ver los resultados

Los gráficos se guardan en la carpeta `output/`:

**Linux / Mac:**
```bash
xdg-open output/wordcloud.png
xdg-open output/sentiment_chart.png
```

**Windows:**
```bash
start output\wordcloud.png
start output\sentiment_chart.png
```

---

## Resultado esperado en consola

```
=======================================================
 PIPELINE DE ANÁLISIS DE SENTIMIENTO — PLN
=======================================================
 Archivo: data/sample_reviews.csv
 10 comentarios cargados.

#    ORIGINAL                  LEMATIZADO           SENTIMIENTO  SCORE
──────────────────────────────────────────────────────────────────────
1    El producto llegó en...   producto llegar...   Positivo     1.0
2    Pésimo servicio...        pésimo servicio...   Negativo    -1.0
...

 Proceso completado. Revisa la carpeta output/
=======================================================
```

Archivos generados:
- `output/wordcloud.png` — nube de palabras lematizadas
- `output/sentiment_chart.png` — gráfico de distribución de sentimientos

---

## Estructura del proyecto

```
eif4200-pid4-nlp/
├── main.py              # Glend — orquesta el pipeline
├── data_loader.py       # Glend — carga CSV/Excel/TXT
├── cleaner.py           # Carranza — limpieza y stop words
├── tokenizer.py         # Dorian — tokenización y lematización
├── sentiment.py         # Jamel — análisis de sentimiento
├── visualizer.py        # Yeye — WordCloud y gráficos
├── data/
│   └── sample_reviews.csv
├── output/              # Se crea automáticamente
├── requirements.txt
└── README.md
```
