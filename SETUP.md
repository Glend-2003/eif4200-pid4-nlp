# Instalación y Ejecución

## Instalar (solo la primera vez)

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_lg-3.7.0/es_core_news_lg-3.7.0-py3-none-any.whl
```

> Necesitas internet la primera vez (descarga los modelos de PLN).

## Ejecutar

```bash
source venv/bin/activate          # activar el entorno en cada terminal nueva
python main.py --input data/resenas_clientes.csv
```

También acepta JSON, Excel o TXT:

```bash
python main.py --input data/resenas_clientes.json
```

## Ver resultados

Se guardan en `output/`:

```bash
xdg-open output/wordcloud.png         # Windows: start output\wordcloud.png
xdg-open output/sentiment_chart.png
```
