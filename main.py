#!/usr/bin/env python3
"""
Ponto de entrada principal do Pipeline ETL.

Uso:
    python main.py

Coloque os arquivos brutos (CSV / Excel) na pasta data/raw/
e execute este script.
"""

from src.etl_pipeline import ETLPipeline


def main():
    pipeline = ETLPipeline(config_path="config/config.yaml")
    pipeline.run()


if __name__ == "__main__":
    main()
