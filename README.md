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
