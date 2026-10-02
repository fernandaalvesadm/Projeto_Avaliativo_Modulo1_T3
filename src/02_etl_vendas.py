"""
02_etl_vendas.py — Fase 3: tratamento com Pandas.
Lê a Bronze, trata os dados, carrega a Silver e salva o CSV tratado.
Execute na pasta principal: python src/02_etl_vendas.py
"""
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from database import get_engine

OUTPUT_CSV = Path(__file__).resolve().parent.parent / "data/processed/vendas_tratadas.csv"

# Nomes da base original -> nomes da base tratada.
MAPA_COLUNAS_TRATADA = {
    "invoice_id": "id_venda",
    "branch": "filial",
    "city": "cidade",
    "customer_type": "tipo_cliente",
    "gender": "genero",
    "product_line": "linha_produto",
    "unit_price": "preco_unitario",
    "quantity": "quantidade",
    "tax_5_percent": "imposto",
    "sales": "valor_total",
    "sale_date": "data_venda",
    "sale_time": "hora_venda",
    "payment": "forma_pagamento",
    "cogs": "custo_mercadoria",
    "gross_margin_percentage": "margem_percentual",
    "gross_income": "receita_bruta",
    "rating": "avaliacao",
}
COLUNAS_FINAIS = list(MAPA_COLUNAS_TRATADA.values())


def extrair_raw():
    """Lê os dados brutos do PostgreSQL."""
    df = pd.read_sql_table("raw_vendas", get_engine(), schema="bronze")
    print(f"Vendas lidas: {len(df)}")
    return df


def tratar_dados(df):
    """Limpa, converte, valida e cria as colunas para análise."""
    df = df.copy()

    # Retira espaços dos textos e transforma textos vazios em valores ausentes.
    textos = ["invoice_id", "branch", "city", "customer_type", "gender",
              "product_line", "payment", "sale_date", "sale_time"]
    for col in textos:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)
    print(f"Campos ausentes encontrados: {df.isna().sum().sum()}")

    # Remove linhas sem identificação/informações obrigatórias e IDs repetidos.
    antes = len(df)
    obrigatorias = ["invoice_id", "branch", "city", "product_line", "payment"]
    df = df.dropna(subset=obrigatorias)
    df = df.drop_duplicates(subset="invoice_id").copy()
    print(f"Linhas removidas por campos obrigatórios vazios ou duplicidade: {antes - len(df)}")
    if df.empty:
        raise ValueError("Não restaram vendas para analisar. Confira a origem.")

    # Converte datas e horários; valores inválidos passam a ser ausentes.
    datas = pd.to_datetime(df["sale_date"], format="%m/%d/%Y", errors="coerce")
    horas = pd.to_datetime(df["sale_time"], format="%I:%M:%S %p", errors="coerce")
    df["sale_date"] = datas.dt.date
    df["sale_time"] = horas.dt.time

    # Converte os números e avisa quando um valor informado é inválido.
    numericas = ["unit_price", "quantity", "tax_5_percent", "sales",
                 "cogs", "gross_margin_percentage", "gross_income", "rating"]
    for col in numericas:
        numeros = pd.to_numeric(df[col], errors="coerce")
        numeros = numeros.replace([float("inf"), float("-inf")], float("nan"))
        if (df[col].notna() & numeros.isna()).any():
            raise ValueError(f"Valor numérico inválido em '{col}'. Confira a origem.")
        df[col] = numeros

    # Valores financeiros ausentes não são substituídos por zero.
    financeiros = ["unit_price", "tax_5_percent", "sales", "cogs", "gross_income"]
    necessarias = financeiros + ["quantity", "sale_date", "sale_time"]
    faltando = df[necessarias].columns[df[necessarias].isna().any()].tolist()
    if faltando:
        raise ValueError(f"Campos necessários ausentes ou inválidos: {faltando}")
    if (df[financeiros] < 0).any().any():
        raise ValueError("Existem valores financeiros negativos. Confira a origem.")
    if ((df["quantity"] <= 0) | (df["quantity"] % 1 != 0)).any():
        raise ValueError("A quantidade deve ser um número inteiro maior que zero.")
    if not df["rating"].dropna().between(0, 10).all():
        raise ValueError("A avaliação deve estar entre 0 e 10.")
    df["quantity"] = df["quantity"].astype(int)
    # Avaliação e margem podem continuar ausentes, conforme o esquema da Silver.

    # Confere o total antes de arredondar: preço × quantidade + imposto.
    calculado = df["unit_price"] * df["quantity"] + df["tax_5_percent"]
    if ((calculado - df["sales"]).abs() > 0.05).any():
        raise ValueError("Há vendas com diferença no total superior a 0,05.")

    # Usa duas casas decimais, com a mesma regra da tabela NUMERIC do banco.
    for col in numericas:
        if col != "quantity":
            df[col] = df[col].map(lambda v: float(Decimal(str(v)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP)) if pd.notna(v) else float("nan"))

    # Colunas derivadas ficam no CSV para apoiar as análises.
    df["dia_semana"] = datas.dt.day_name()
    df["mes"] = datas.dt.month
    df["periodo_dia"] = horas.dt.hour.map(
        lambda h: "Manhã" if h < 12 else ("Tarde" if h < 18 else "Noite"))
    return df.rename(columns=MAPA_COLUNAS_TRATADA)


def salvar_dados(df):
    """Carrega a Silver e salva o CSV; mantém a estrutura atual das tabelas."""
    # Na mesma transação: se a inserção falhar, a limpeza é desfeita.
    with get_engine().begin() as conn:
        conn.execute(text("TRUNCATE TABLE silver.vendas_tratada"))
        df[COLUNAS_FINAIS].to_sql("vendas_tratada", conn, schema="silver",
                                if_exists="append", index=False)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Vendas tratadas e salvas: {len(df)}")
    print(f"CSV: {OUTPUT_CSV}")


def main():
    df = extrair_raw()
    df = tratar_dados(df)
    salvar_dados(df)


if __name__ == "__main__":
    main()
