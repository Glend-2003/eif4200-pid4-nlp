"""
data_loader.py — Carga de archivos CSV, Excel y TXT para el pipeline de PLN.
Responsable: Glend
"""
import os
import logging

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Nombres de columna reconocidos como texto de reseña
_COLUMNAS_TEXTO = {"review", "comment", "text", "comentario", "reseña"}


def load_data(filepath: str) -> list:
    """
    Carga reseñas desde un archivo CSV, Excel, JSON o TXT.

    Detecta automáticamente la columna de texto en archivos tabulares.
    Retorna una lista de strings con el contenido de cada fila o línea.

    Args:
        filepath: Ruta al archivo de entrada.

    Returns:
        Lista de strings con las reseñas cargadas. Lista vacía si falla.
    """
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".csv":
            return _load_csv(filepath)
        elif ext in (".xlsx", ".xls"):
            return _load_excel(filepath)
        elif ext == ".json":
            return _load_json(filepath)
        elif ext == ".txt":
            return _load_txt(filepath)
        else:
            logger.error(f"Formato no soportado: '{ext}'. Use CSV, Excel, JSON o TXT.")
            return []
    except Exception as e:
        logger.error(f"Error inesperado al cargar '{filepath}': {e}")
        return []


def _load_csv(filepath: str) -> list:
    """
    Carga un archivo CSV y extrae la columna de texto detectada.

    Args:
        filepath: Ruta al archivo CSV.

    Returns:
        Lista de strings con los valores de la columna de texto.
    """
    try:
        import pandas as pd
        df = pd.read_csv(filepath, encoding="utf-8")
        col = _find_text_column(df)
        registros = df[col].dropna().astype(str).tolist()
        logger.info(f"CSV cargado — columna '{col}', {len(registros)} registros.")
        return registros
    except UnicodeDecodeError:
        # Reintento con codificación latin-1 para archivos con caracteres especiales
        import pandas as pd
        df = pd.read_csv(filepath, encoding="latin-1")
        col = _find_text_column(df)
        registros = df[col].dropna().astype(str).tolist()
        logger.info(f"CSV cargado (latin-1) — columna '{col}', {len(registros)} registros.")
        return registros
    except Exception as e:
        logger.error(f"Error al leer CSV '{filepath}': {e}")
        return []


def _load_excel(filepath: str) -> list:
    """
    Carga un archivo Excel (.xlsx o .xls) y extrae la columna de texto detectada.

    Args:
        filepath: Ruta al archivo Excel.

    Returns:
        Lista de strings con los valores de la columna de texto.
    """
    try:
        import pandas as pd
        df = pd.read_excel(filepath)
        col = _find_text_column(df)
        registros = df[col].dropna().astype(str).tolist()
        logger.info(f"Excel cargado — columna '{col}', {len(registros)} registros.")
        return registros
    except ImportError:
        logger.error("Falta la dependencia 'openpyxl'. Instálela con: pip install openpyxl")
        return []
    except Exception as e:
        logger.error(f"Error al leer Excel '{filepath}': {e}")
        return []


def _load_json(filepath: str) -> list:
    """
    Carga un archivo JSON con reseñas y extrae el texto de cada registro.

    Soporta tres estructuras comunes de auditoría de clientes:
        - Lista de textos:        ["reseña 1", "reseña 2", ...]
        - Lista de objetos:       [{"review": "..."}, {"comentario": "..."}, ...]
        - Objeto que envuelve la lista: {"reviews": [ ... ]}

    Args:
        filepath: Ruta al archivo JSON.

    Returns:
        Lista de strings con las reseñas. Lista vacía si falla.
    """
    import json
    try:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except UnicodeDecodeError:
            # Reintento con codificación latin-1
            with open(filepath, "r", encoding="latin-1") as f:
                data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSON inválido en '{filepath}': {e}")
        return []
    except Exception as e:
        logger.error(f"Error al leer JSON '{filepath}': {e}")
        return []

    return _extract_from_json(data)


def _extract_from_json(data) -> list:
    """
    Normaliza una estructura JSON ya parseada a una lista de reseñas.

    Args:
        data: Objeto Python resultante de json.load (dict o list).

    Returns:
        Lista de strings con las reseñas.
    """
    # Si es un dict, buscamos la primera lista anidada (ej. {"reviews": [...]});
    # si no hay ninguna, lo tratamos como un registro único.
    if isinstance(data, dict):
        anidada = next((v for v in data.values() if isinstance(v, list)), None)
        data = anidada if anidada is not None else [data]

    if not isinstance(data, list):
        logger.error("Estructura JSON no soportada. Se espera una lista de reseñas u objetos.")
        return []

    if not data:
        logger.warning("El archivo JSON no contiene registros.")
        return []

    # Caso 1: lista de strings.
    if all(isinstance(x, str) for x in data):
        registros = [x for x in data if x.strip()]
        logger.info(f"JSON cargado — {len(registros)} reseñas (lista de texto).")
        return registros

    # Caso 2: lista de objetos -> reutilizamos la detección de columna de pandas.
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        col = _find_text_column(df)
        registros = df[col].dropna().astype(str).tolist()
        logger.info(f"JSON cargado — campo '{col}', {len(registros)} registros.")
        return registros
    except Exception as e:
        logger.error(f"No se pudo interpretar el JSON como tabla de objetos: {e}")
        return []


def _load_txt(filepath: str) -> list:
    """
    Carga un archivo de texto plano; cada línea no vacía es una reseña.

    Args:
        filepath: Ruta al archivo TXT.

    Returns:
        Lista de strings, una por línea con contenido.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lineas = [l.strip() for l in f if l.strip()]
        logger.info(f"TXT cargado — {len(lineas)} líneas.")
        return lineas
    except UnicodeDecodeError:
        # Reintento con codificación latin-1
        with open(filepath, "r", encoding="latin-1") as f:
            lineas = [l.strip() for l in f if l.strip()]
        logger.info(f"TXT cargado (latin-1) — {len(lineas)} líneas.")
        return lineas
    except Exception as e:
        logger.error(f"Error al leer TXT '{filepath}': {e}")
        return []


def _find_text_column(df) -> str:
    """
    Detecta la columna que contiene el texto de las reseñas.

    Primero busca entre los nombres candidatos conocidos; si no encuentra
    ninguno, usa la primera columna de tipo objeto (string).

    Args:
        df: DataFrame de pandas.

    Returns:
        Nombre de la columna seleccionada.
    """
    # Búsqueda por nombre conocido (insensible a mayúsculas)
    for col in df.columns:
        if col.strip().lower() in _COLUMNAS_TEXTO:
            return col

    # Fallback: primera columna de tipo objeto
    for col in df.columns:
        if df[col].dtype == object:
            logger.warning(
                f"Columna de texto no reconocida. Usando la columna '{col}' por defecto."
            )
            return col

    # Último recurso: primera columna del DataFrame
    logger.warning("No se encontró columna de texto. Usando la primera columna disponible.")
    return df.columns[0]
