"""
Gera arquivos de exemplo (sujos) para testar o pipeline.
Execute: python scripts/generate_sample_data.py
"""

from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def generate():
    # Arquivo 1 - Vendas (com problemas comuns)
    vendas = pd.DataFrame({
        "Data Venda": ["01/03/2024", "02/03/2024", "02/03/2024", "03/03/2024", None, "  "],
        "Cliente": ["  João Silva  ", "Maria Souza", "Maria Souza", "Pedro Costa", "Ana Lima", ""],
        "Valor (R$)": ["1.250,90", "890,00", "890,00", "2.100,50", "450,00", ""],
        "Quantidade": [2, 1, 1, 3, 1, None],
        "  Região  ": ["Sul", "Sudeste", "Sudeste", "Norte", "Nordeste", "Centro-Oeste"],
        "Observação": ["", "Cliente VIP", None, "  ", "Promoção", "Erro"],
    })
    vendas.to_csv(RAW_DIR / "vendas_marco.csv", index=False, encoding="latin1", sep=";")

    # Arquivo 2 - Outro CSV com encoding diferente e colunas parecidas
    vendas2 = pd.DataFrame({
        "data_venda": ["05/03/2024", "06/03/2024", "07/03/2024"],
        "cliente": ["Carlos Mendes", "Fernanda Alves", "Ricardo Dias"],
        "valor": [1500.00, 320.50, 980.00],
        "qtd": [1, 2, 1],
        "regiao": ["Sul", "Sudeste", "Sul"],
    })
    vendas2.to_csv(RAW_DIR / "vendas_abril.csv", index=False, encoding="utf-8")

    # Arquivo 3 - Excel
    estoque = pd.DataFrame({
        "Código Produto": ["P001", "P002", "P003", "P001", "P004"],
        "Nome do Produto": ["  Notebook  ", "Mouse", "Teclado", "Notebook", "Monitor"],
        "Preço Unitário": [3500.00, 89.90, 150.00, 3500.00, 899.00],
        "Estoque Atual": [12, 45, 30, 12, 8],
        "Categoria": ["Informática", "Periféricos", "Periféricos", "Informática", "Informática"],
        "Coluna Vazia": [None, None, None, None, None],
    })
    estoque.to_excel(RAW_DIR / "estoque.xlsx", index=False)

    print("✅ Arquivos de exemplo gerados em data/raw/")
    print("   - vendas_marco.csv  (delimitador ; | latin1 | dados sujos)")
    print("   - vendas_abril.csv  (utf-8 | limpo)")
    print("   - estoque.xlsx      (com coluna vazia e duplicata)")


if __name__ == "__main__":
    generate()
