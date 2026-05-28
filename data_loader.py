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
