# Automação de ETL e Tratamento de Dados com Python (Pandas)

Pipeline completo de **ETL (Extract, Transform, Load)** desenvolvido em Python com Pandas para **limpeza, padronização e consolidação** de arquivos brutos em CSV e Excel.

O projeto foi criado para **eliminar rotinas manuais repetitivas**, reduzir tempo de processamento e **minimizar falhas operacionais** no tratamento de dados.

---

## Objetivo

- Ler automaticamente múltiplos arquivos CSV e Excel de uma pasta
- Aplicar limpeza padronizada (duplicatas, nulos, espaços, nomes de colunas, tipos)
- Gerar versões processadas individuais
- Consolidar todos os arquivos em um único dataset final
- Registrar logs detalhados de toda a execução

---

## Estrutura do Projeto

```
etl-automation/
├── config/
│   └── config.yaml          # Configurações centralizadas
├── data/
│   ├── raw/                 # Coloque aqui os arquivos brutos
│   ├── processed/           # Arquivos limpos individuais
│   └── consolidated/        # Resultado consolidado final
├── logs/                    # Logs de execução
├── scripts/
│   └── generate_sample_data.py
├── src/
│   ├── __init__.py
│   ├── data_cleaner.py      # Regras de limpeza e padronização
│   ├── etl_pipeline.py      # Orquestrador do pipeline
│   └── utils.py             # Funções auxiliares
├── main.py                  # Ponto de entrada
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/etl-automation.git
cd etl-automation

# 2. Crie e ative o ambiente virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt
```

---

## Como Usar

### 1. Coloque os arquivos brutos

Coloque todos os arquivos `.csv`, `.xlsx` ou `.xls` na pasta:

```
data/raw/
```

### 2. (Opcional) Ajuste as configurações

Edite o arquivo `config/config.yaml` conforme sua necessidade:

- Estratégia de preenchimento de nulos
- Conversão de tipos de colunas
- Nome e formato do arquivo consolidado
- Nível de log

### 3. Execute o pipeline

```bash
python main.py
```

### 4. Resultados

| Pasta | Conteúdo |
|-------|----------|
| `data/processed/` | Um arquivo CSV limpo para cada arquivo de origem |
| `data/consolidated/` | Dataset único consolidado (CSV e/ou Excel) |
| `logs/` | Log detalhado da execução |

---

## O que o pipeline faz automaticamente

| Etapa | Ação |
|-------|------|
| **Extração** | Detecta encoding e separador de CSVs; lê Excel (xlsx/xls) |
| **Limpeza** | Remove duplicatas, linhas/colunas vazias, espaços extras |
| **Padronização** | Normaliza nomes de colunas (minúsculas, sem acento, underscore) |
| **Tipos** | Conversão configurável (datetime, float, int, str) |
| **Rastreabilidade** | Adiciona coluna `arquivo_origem` |
| **Consolidação** | Une todos os arquivos em um único dataset |
| **Logging** | Registra tudo em console + arquivo |

---

## Gerar dados de exemplo (para teste)

```bash
python scripts/generate_sample_data.py
python main.py
```

Isso cria 3 arquivos com problemas comuns (encoding diferente, delimitador `;`, espaços, duplicatas, colunas vazias etc.) e processa tudo automaticamente.

---

## Personalização rápida

### Converter tipos específicos

No `config/config.yaml`:

```yaml
type_casting:
  data_venda: "datetime"
  valor: "float"
  quantidade: "int"
```

### Mudar estratégia de nulos

```yaml
cleaning:
  fillna_strategy: 0          # preenche com zero
  # ou "ffill" / "bfill"
```

### Formato de saída consolidada

```yaml
consolidation:
  output_format: "both"       # csv | xlsx | both
  output_filename: "base_final"
```

---

## Tecnologias

- **Python 3.9+**
- **Pandas** – manipulação de dados
- **OpenPyXL / xlrd** – leitura de Excel
- **PyYAML** – configuração
- **tqdm** – barra de progresso

---

## Benefícios operacionais

- Reduz drasticamente o tempo de tratamento manual
- Padronização consistente entre diferentes fontes
- Elimina erros humanos recorrentes (espaços, encoding, duplicatas)
- Rastreabilidade completa via logs e coluna de origem
- Fácil de manter e evoluir (tudo configurável via YAML)

---

## Licença

MIT License – use livremente em projetos pessoais ou corporativos.

---

## Autor

Desenvolvido por **Edison de Souza Garcia** (https://www.linkedin.com/in/edison-garcia-2b1055214/).
