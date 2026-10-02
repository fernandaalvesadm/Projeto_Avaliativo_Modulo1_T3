"""
01_leitura_dados.py

Fase 1 - Extração e Carga Raw.

Lê o CSV original (data/raw/SuperMarket_Analysis.csv), faz uma inspeção
estrutural inicial com Pandas (tipos, nulos, duplicidades, estatísticas
descritivas básicas) e carrega os dados, SEM ALTERAR O CONTEÚDO, na tabela
bronze.raw_vendas do PostgreSQL (Camada Bronze/Raw).
Depois, exporta a consulta por filial para CSV e lê o resultado com Pandas.

Executar (a partir da raiz do projeto):
    python src/01_leitura_dados.py
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from database import get_engine

RAW_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "SuperMarket_Analysis.csv"
CONSULTA_CSV_PATH = RAW_CSV_PATH.parent / "consulta_faturamento_por_filial.csv"

# Nomes das colunas no CSV original -> nomes das colunas na tabela bronze.raw_vendas.
# Mantém a Camada Raw fiel ao dado original, só padronizando os nomes das
# colunas (snake_case) para facilitar o trabalho em SQL.
MAPA_COLUNAS_RAW = {
    "Invoice ID": "invoice_id",
    "Branch": "branch",
    "City": "city",
    "Customer type": "customer_type",
    "Gender": "gender",
    "Product line": "product_line",
    "Unit price": "unit_price",
    "Quantity": "quantity",
    "Tax 5%": "tax_5_percent",
    "Sales": "sales",
    "Date": "sale_date",
    "Time": "sale_time",
    "Payment": "payment",
    "cogs": "cogs",
    "gross margin percentage": "gross_margin_percentage",
    "gross income": "gross_income",
    "Rating": "rating",
}


def ler_csv() -> pd.DataFrame:
    """Lê o CSV sem tratamento; o Pandas reconhece os tipos automaticamente."""
    if not RAW_CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV não encontrado em {RAW_CSV_PATH}. Baixe o dataset "
            "'Supermarket Sales' do Kaggle e salve-o nesse caminho."
        )
    df = pd.read_csv(RAW_CSV_PATH)
    df = df.rename(columns=MAPA_COLUNAS_RAW)
    return df


def inspecionar(df: pd.DataFrame) -> None:
    """Inspeção estrutural inicial: shape, tipos, nulos, duplicidades e
    estatísticas descritivas básicas das colunas numéricas."""
    print("=" * 70)
    print("INSPEÇÃO INICIAL DO CSV BRUTO")
    print("=" * 70)

    print(f"\nLinhas x Colunas: {df.shape}")

    print("\nTipos de dados (dtype) por coluna:")
    print(df.dtypes)

    print("\nValores nulos por coluna:")
    nulos = df.isna().sum()
    print(nulos[nulos > 0] if nulos.sum() > 0 else "Nenhum valor nulo encontrado.")

    print(f"\nLinhas duplicadas (todas as colunas iguais): {df.duplicated().sum()}")
    print(f"IDs de venda duplicados (invoice_id): {df['invoice_id'].duplicated().sum()}")

    print("\nEstatísticas descritivas (colunas numéricas):")
    print(df.describe().T)

    print("\nValores únicos em colunas categóricas:")
    for col in ["branch", "city", "customer_type", "gender", "product_line", "payment"]:
        print(f"  {col}: {sorted(df[col].dropna().unique())}")


def carregar_raw(df: pd.DataFrame) -> None:
    """Carrega o DataFrame, sem alterações de conteúdo, na tabela
    bronze.raw_vendas.

    A tabela e suas constraints (PRIMARY KEY, tipos) já foram criadas pelo
    script sql/02_criar_tabelas.sql (Fase 0). Aqui apenas limpamos o
    conteúdo (TRUNCATE) e inserimos os dados novamente (APPEND), para que
    o pipeline seja idempotente sem perder a estrutura/constraints da
    tabela a cada execução.
    """
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE bronze.raw_vendas"))
        # A inserção usa a mesma transação: se falhar, a limpeza é desfeita.
        df.to_sql("raw_vendas", conn, schema="bronze", if_exists="append", index=False)
    print(f"\n{len(df)} linhas carregadas em 'bronze.raw_vendas' (Camada Bronze/Raw) no PostgreSQL.")


def exportar_e_ler_consulta() -> None:
    """Executa a consulta 2 do SQL, exporta para CSV e lê com Pandas."""
    consulta = text("""
        SELECT branch, COUNT(*) AS qtd_vendas,
               SUM(sales) AS faturamento_total, AVG(sales) AS ticket_medio
        FROM bronze.raw_vendas
        GROUP BY branch
        ORDER BY faturamento_total DESC;
    """)
    resultado = pd.read_sql_query(consulta, get_engine())
    resultado.to_csv(CONSULTA_CSV_PATH, index=False)

    # Lê o CSV exportado, sem substituir o DataFrame da base original.
    df_consulta = pd.read_csv(CONSULTA_CSV_PATH)
    print("\nCONFERÊNCIA DO CSV EXPORTADO DA CONSULTA SQL")
    print(df_consulta)
    print("\nTipos das colunas:")
    print(df_consulta.dtypes)
    print("\nValores nulos por coluna:")
    print(df_consulta.isna().sum())
    print("\nEstatísticas do resultado exportado:")
    print(df_consulta.describe())
    print(f"\nTotal de vendas na consulta: {df_consulta['qtd_vendas'].sum()}")
    print(f"CSV exportado e lido: {CONSULTA_CSV_PATH}")


def main() -> None:
    df = ler_csv()
    inspecionar(df)
    carregar_raw(df)
    exportar_e_ler_consulta()


if __name__ == "__main__":
    main()