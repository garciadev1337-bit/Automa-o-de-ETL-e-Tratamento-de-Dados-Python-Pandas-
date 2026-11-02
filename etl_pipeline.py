"""
Pipeline principal de ETL.
Lê, limpa, padroniza e consolida arquivos CSV e Excel.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
from tqdm import tqdm

from .data_cleaner import DataCleaner
from .utils import (
    detect_encoding,
    get_files,
    load_config,
    setup_logging,
)


class ETLPipeline:
    """Orquestra todo o fluxo de ETL."""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.logger = setup_logging(
            log_dir=self.config["paths"]["logs"],
            level=self.config.get("logging", {}).get("level", "INFO"),
            save_to_file=self.config.get("logging", {}).get("save_to_file", True),
        )
        self.cleaner = DataCleaner(self.config, logger=self.logger)

        # Garante que os diretórios existam
        for key in ["raw", "processed", "consolidated", "logs"]:
            Path(self.config["paths"][key]).mkdir(parents=True, exist_ok=True)

    def run(self) -> Optional[pd.DataFrame]:
        """Executa o pipeline completo."""
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO PIPELINE ETL")
        self.logger.info("=" * 60)

        raw_path = Path(self.config["paths"]["raw"])
        extensions = self.config.get("supported_extensions", [".csv", ".xlsx", ".xls"])

        files = get_files(raw_path, extensions)

        if not files:
            self.logger.warning(f"Nenhum arquivo encontrado em: {raw_path}")
            self.logger.info("Coloque arquivos CSV ou Excel na pasta data/raw e execute novamente.")
            return None

        self.logger.info(f"Arquivos encontrados: {len(files)}")
        for f in files:
            self.logger.info(f"  • {f.name}")

        cleaned_dfs = []
        errors = []

        for file_path in tqdm(files, desc="Processando arquivos", unit="arquivo"):
            try:
                df = self._read_file(file_path)
                if df is None or df.empty:
                    self.logger.warning(f"Arquivo vazio ou ilegível: {file_path.name}")
                    continue

                df_clean = self.cleaner.clean(df, source_name=file_path.name)

                # Adiciona coluna de origem (opcional)
                if self.config.get("consolidation", {}).get("add_source_column", True):
                    df_clean["arquivo_origem"] = file_path.name

                # Salva versão processada individual
                self._save_processed(df_clean, file_path)

                cleaned_dfs.append(df_clean)

            except Exception as e:
                msg = f"Erro ao processar {file_path.name}: {e}"
                self.logger.error(msg)
                errors.append(msg)

        if not cleaned_dfs:
            self.logger.error("Nenhum arquivo foi processado com sucesso.")
            return None

        # Consolidação
        consolidated = None
        if self.config.get("consolidation", {}).get("enabled", True):
            consolidated = self._consolidate(cleaned_dfs)

        self.logger.info("=" * 60)
        self.logger.info("PIPELINE FINALIZADO")
        self.logger.info(f"  Arquivos processados com sucesso: {len(cleaned_dfs)}")
        self.logger.info(f"  Arquivos com erro: {len(errors)}")
        if consolidated is not None:
            self.logger.info(f"  Linhas no consolidado: {len(consolidated)}")
        self.logger.info("=" * 60)

        return consolidated

    def _read_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Lê um arquivo CSV ou Excel com tratamento robusto."""
        suffix = file_path.suffix.lower()
        self.logger.info(f"Lendo: {file_path.name}")

        try:
            if suffix == ".csv":
                encoding = detect_encoding(file_path)
                # Detecta separador automaticamente (mais robusto)
                # Tenta os separadores mais comuns e escolhe o que gera mais colunas
                best_df = None
                best_cols = 0
                for candidate_sep in [",", ";", "\t", "|"]:
                    try:
                        df_try = pd.read_csv(
                            file_path,
                            encoding=encoding,
                            sep=candidate_sep,
                            decimal=self.config.get("read_options", {}).get("csv", {}).get("decimal", "."),
                            low_memory=False,
                        )
                        if df_try.shape[1] > best_cols:
                            best_df = df_try
                            best_cols = df_try.shape[1]
                    except Exception:
                        continue

                if best_df is None or best_cols <= 1:
                    # Último recurso: engine python com detecção automática
                    best_df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        sep=None,
                        engine="python",
                        low_memory=False,
                    )

                return best_df

            elif suffix in (".xlsx", ".xls"):
                engine = "openpyxl" if suffix == ".xlsx" else "xlrd"
                # Lê a primeira planilha por padrão
                df = pd.read_excel(file_path, engine=engine)
                return df

            else:
                self.logger.warning(f"Extensão não suportada: {suffix}")
                return None

        except Exception as e:
            self.logger.error(f"Falha na leitura de {file_path.name}: {e}")
            raise

    def _save_processed(self, df: pd.DataFrame, original_path: Path) -> None:
        """Salva o DataFrame limpo na pasta processed."""
        processed_dir = Path(self.config["paths"]["processed"])
        output_name = f"{original_path.stem}_limpo.csv"
        output_path = processed_dir / output_name

        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        self.logger.info(f"  → Salvo processado: {output_name}")

    def _consolidate(self, dfs: list[pd.DataFrame]) -> pd.DataFrame:
        """Consolida todos os DataFrames em um único arquivo."""
        self.logger.info("Iniciando consolidação...")

        # Alinha colunas (união de todas)
        consolidated = pd.concat(dfs, ignore_index=True, sort=False)

        # Ordenação opcional
        sort_col = self.config.get("consolidation", {}).get("sort_by")
        if sort_col and sort_col in consolidated.columns:
            consolidated = consolidated.sort_values(by=sort_col)

        # Exporta
        out_dir = Path(self.config["paths"]["consolidated"])
        base_name = self.config.get("consolidation", {}).get("output_filename", "dados_consolidados")
        fmt = self.config.get("consolidation", {}).get("output_format", "xlsx").lower()

        if fmt in ("csv", "both"):
            csv_path = out_dir / f"{base_name}.csv"
            consolidated.to_csv(csv_path, index=False, encoding="utf-8-sig")
            self.logger.info(f"  → Consolidado CSV: {csv_path.name}")

        if fmt in ("xlsx", "both"):
            xlsx_path = out_dir / f"{base_name}.xlsx"
            consolidated.to_excel(xlsx_path, index=False, engine="openpyxl")
            self.logger.info(f"  → Consolidado Excel: {xlsx_path.name}")

        return consolidated


def main():
    """Ponto de entrada do script."""
    pipeline = ETLPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
