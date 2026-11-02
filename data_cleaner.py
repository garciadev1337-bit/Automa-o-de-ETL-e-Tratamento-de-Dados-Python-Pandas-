"""
Módulo de limpeza e padronização de dados.
"""

from typing import Optional

import pandas as pd

from .utils import normalize_column_name


class DataCleaner:
    """Responsável pela limpeza e padronização de DataFrames."""

    def __init__(self, config: dict, logger=None):
        self.config = config.get("cleaning") or {}
        self.type_casting = config.get("type_casting") or {}
        self.logger = logger

    def clean(self, df: pd.DataFrame, source_name: str = "") -> pd.DataFrame:
        """
        Aplica todas as regras de limpeza e padronização em um DataFrame.
        """
        if df.empty:
            if self.logger:
                self.logger.warning(f"DataFrame vazio recebido de: {source_name}")
            return df

        original_shape = df.shape
        df = df.copy()

        # 1. Padronizar nomes de colunas
        if self.config.get("standardize_column_names", True):
            df.columns = [normalize_column_name(col) for col in df.columns]
            # Resolve colunas duplicadas após normalização
            df = self._resolve_duplicate_columns(df)

        # 2. Substituir strings vazias por NaN
        if self.config.get("replace_empty_with_nan", True):
            df = df.replace(r"^\s*$", pd.NA, regex=True)

        # 3. Remover espaços em strings
        if self.config.get("strip_strings", True):
            str_cols = df.select_dtypes(include=["object", "string"]).columns
            for col in str_cols:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "NaT": pd.NA})

        # 4. Remover linhas completamente vazias
        if self.config.get("drop_completely_empty_rows", True):
            df = df.dropna(how="all")

        # 5. Remover colunas completamente vazias
        if self.config.get("drop_completely_empty_columns", True):
            df = df.dropna(axis=1, how="all")

        # 6. Remover duplicatas
        if self.config.get("remove_duplicates", True):
            before = len(df)
            df = df.drop_duplicates()
            removed = before - len(df)
            if removed > 0 and self.logger:
                self.logger.info(f"  → {removed} duplicata(s) removida(s) de '{source_name}'")

        # 7. Estratégia de preenchimento de nulos (opcional)
        fillna = self.config.get("fillna_strategy")
        if fillna is not None:
            if fillna in ("ffill", "bfill"):
                df = df.fillna(method=fillna)
            else:
                df = df.fillna(fillna)

        # 8. Cast de tipos (se configurado)
        df = self._apply_type_casting(df)

        if self.logger:
            self.logger.info(
                f"  Limpeza de '{source_name}': {original_shape} → {df.shape}"
            )

        return df.reset_index(drop=True)

    def _resolve_duplicate_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Renomeia colunas duplicadas adicionando sufixo numérico."""
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            idxs = cols[cols == dup].index.tolist()
            for i, idx in enumerate(idxs[1:], start=1):
                cols[idx] = f"{dup}_{i}"
        df.columns = cols
        return df

    def _apply_type_casting(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica conversão de tipos definida no config."""
        for col, dtype in self.type_casting.items():
            if col not in df.columns:
                continue
            try:
                if dtype == "datetime":
                    df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
                elif dtype == "float":
                    df[col] = (
                        df[col]
                        .astype(str)
                        .str.replace(",", ".", regex=False)
                        .str.replace(r"[^\d.-]", "", regex=True)
                    )
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                elif dtype == "int":
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                elif dtype == "str":
                    df[col] = df[col].astype(str)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"  Falha ao converter coluna '{col}' para {dtype}: {e}")
        return df
