"""
Testes básicos do DataCleaner.
Execute: python -m pytest tests/ -v
(ou simplesmente rode este arquivo)
"""

import sys
from pathlib import Path

import pandas as pd

# Garante que o src está no path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data_cleaner import DataCleaner
from src.utils import normalize_column_name


def test_normalize_column_name():
    assert normalize_column_name("  Data Venda  ") == "data_venda"
    assert normalize_column_name("Valor (R$)") == "valor_r"
    assert normalize_column_name("Código do Cliente") == "codigo_do_cliente"
    assert normalize_column_name("Região") == "regiao"
    print("✅ test_normalize_column_name passou")


def test_cleaner_basic():
    config = {
        "cleaning": {
            "remove_duplicates": True,
            "drop_completely_empty_rows": True,
            "drop_completely_empty_columns": True,
            "strip_strings": True,
            "replace_empty_with_nan": True,
            "standardize_column_names": True,
            "fillna_strategy": None,
        },
        "type_casting": {},
    }

    df = pd.DataFrame({
        "  Nome  ": ["  João  ", "Maria", "João", "  ", None],
        "Valor": [100, 200, 100, None, 300],
        "Vazia": [None, None, None, None, None],
    })

    cleaner = DataCleaner(config)
    result = cleaner.clean(df, source_name="teste")

    assert "nome" in result.columns
    assert "valor" in result.columns
    assert "vazia" not in result.columns          # coluna vazia removida
    assert len(result) == 3                       # duplicata + linha vazia removidas
    assert result["nome"].iloc[0] == "João"       # espaços removidos
    print("✅ test_cleaner_basic passou")


if __name__ == "__main__":
    test_normalize_column_name()
    test_cleaner_basic()
    print("\nTodos os testes passaram!")
