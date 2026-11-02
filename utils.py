"""
Utilitários gerais do pipeline ETL.
"""

import logging
import re
import unicodedata
from pathlib import Path
from typing import Optional

import yaml


def setup_logging(log_dir: str = "logs", level: str = "INFO", save_to_file: bool = True) -> logging.Logger:
    """Configura o logger do pipeline."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("etl_pipeline")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    # Arquivo
    if save_to_file:
        from datetime import datetime
        log_file = Path(log_dir) / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Carrega o arquivo de configuração YAML."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalize_column_name(name: str) -> str:
    """
    Padroniza nome de coluna:
    - Remove acentos
    - Converte para minúsculas
    - Substitui espaços e caracteres especiais por underscore
    - Remove underscores duplicados
    """
    if not isinstance(name, str):
        name = str(name)

    # Remove acentos
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))

    # Minúsculas e substituições
    name = name.lower().strip()
    name = re.sub(r"[^\w\s]", "", name)          # remove pontuação
    name = re.sub(r"\s+", "_", name)             # espaços → _
    name = re.sub(r"_+", "_", name)              # underscores duplicados
    name = name.strip("_")

    return name or "coluna_sem_nome"


def detect_encoding(file_path: Path) -> str:
    """Tenta detectar a codificação do arquivo CSV."""
    encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                f.read(1024)
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return "utf-8"  # fallback


def get_files(directory: str | Path, extensions: list[str]) -> list[Path]:
    """Retorna lista de arquivos com as extensões suportadas."""
    directory = Path(directory)
    if not directory.exists():
        return []

    files = []
    for ext in extensions:
        files.extend(directory.glob(f"*{ext}"))
        files.extend(directory.glob(f"*{ext.upper()}"))

    # Remove duplicatas e ordena
    return sorted(set(files))
