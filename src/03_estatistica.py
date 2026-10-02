"""
03_estatistica.py — Fase 4: análise e resultados (Gold).
Responde às oito perguntas, salva estatísticas, quatro gráficos e um notebook.
Execute na pasta principal: python src/03_estatistica.py
Os valores monetários usam a unidade da base, sem conversão de moeda.
"""
from pathlib import Path
import base64
import json

import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text
from database import get_engine

RESULTADOS_DIR = Path(__file__).resolve().parent.parent / "resultados"
ESTATISTICAS_DIR = RESULTADOS_DIR / "estatisticas"
GRAFICOS_DIR = RESULTADOS_DIR / "graficos"
ESTATISTICAS_DIR.mkdir(parents=True, exist_ok=True)
GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

DIAS_SEMANA_PT = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira", "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo",
}


def numero_br(valor):
    """Mostra números no formato brasileiro, por exemplo: 1.042,65."""
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def salvar_grafico(ax, titulo, nome, eixo_x, eixo_y):
    """Finaliza e salva o gráfico, evitando repetir os mesmos comandos."""
    ax.set_title(titulo)
    ax.set_xlabel(eixo_x)
    ax.set_ylabel(eixo_y)
    ax.figure.tight_layout()
    ax.figure.savefig(GRAFICOS_DIR / nome, dpi=150)
    plt.close(ax.figure)


def salvar_notebook(respostas, texto_hipoteses, estatisticas):
    """Monta o notebook com textos, códigos de análise e gráficos."""
    celulas = []

    def texto(conteudo):
        celulas.append({"cell_type": "markdown", "metadata": {}, "source": conteudo})

    def codigo(conteudo):
        celulas.append({"cell_type": "code", "metadata": {}, "source": conteudo,
                        "execution_count": None, "outputs": []})

    texto("# Análise das vendas de supermercado\n\n"
          "Aqui apresento as oito perguntas da atividade e os resultados da análise. "
          "Usei a base tratada, com os valores na unidade monetária original.\n\n"
          "Este notebook é gerado pelo `03_estatistica.py`. Os resultados nos textos "
          "e os gráficos correspondem à execução desse script. As células de código "
          "podem ser executadas para conferir os cálculos.\n\n"
          "Para atualizar todo o relatório, execute o script novamente. "
          "Isso substitui as alterações feitas diretamente no notebook.")
    texto("## Leitura da base tratada\n\nPrimeiro, abro o CSV salvo na etapa de tratamento.")
    codigo("from pathlib import Path\nimport pandas as pd\n\n"
           "# Localiza o projeto, tanto pela pasta principal quanto por resultados.\n"
           "raiz = next(p for p in [Path.cwd(), *Path.cwd().parents]\n"
           "            if (p / 'data/processed/vendas_tratadas.csv').exists())\n"
           "df = pd.read_csv(raiz / 'data/processed/vendas_tratadas.csv')\n"
           "df['data_venda'] = pd.to_datetime(df['data_venda'])\n"
           f"dias = {DIAS_SEMANA_PT!r}\n"
           "df['dia_semana'] = df['data_venda'].dt.day_name().map(dias)\n"
           "df.head()")

    perguntas = [
        ("Qual filial apresentou o maior faturamento?",
         "df.groupby('filial')['valor_total'].sum().sort_values(ascending=False)",
         "Somei o valor das vendas de cada filial para comparar o faturamento."),
        ("Qual filial realizou a maior quantidade de vendas?",
         "df.groupby('filial')['id_venda'].count().sort_values(ascending=False)",
         "Contei os registros de venda de cada filial, sem somar as unidades vendidas."),
        ("Qual linha de produto apresentou o maior faturamento?",
         "df.groupby('linha_produto')['valor_total'].sum().sort_values(ascending=False)",
         "Agrupei as vendas por linha de produto e somei os valores."),
        ("Qual linha de produto recebeu a melhor avaliação média?",
         "df.groupby('linha_produto')['avaliacao'].mean().sort_values(ascending=False)",
         "Calculei a média das avaliações de cada linha de produto."),
        ("Qual foi a forma de pagamento mais utilizada?",
         "df['forma_pagamento'].value_counts()",
         "Contei quantas vendas foram realizadas com cada forma de pagamento."),
        ("Qual foi o valor médio das vendas?",
         "round(df['valor_total'].mean(), 2)",
         "Calculei a média do valor total das vendas."),
        ("Qual foi a maior venda registrada?",
         "df.loc[df['valor_total'].idxmax(),\n"
         "       ['id_venda', 'filial', 'linha_produto', 'valor_total']]",
         "Localizei a venda com o maior valor e mostrei suas informações."),
        ("Em qual dia da semana ocorreu a maior quantidade de vendas?",
         "df['dia_semana'].value_counts()",
         "Identifiquei o dia da semana de cada venda e contei os registros."),
    ]
    for numero, (pergunta, calculo, explicacao) in enumerate(perguntas, start=1):
        texto(f"## {numero}. {pergunta}\n\n{explicacao}")
        codigo(calculo)
        texto(f"**Resultado:** {respostas[numero - 1].split(') ', 1)[1]}")

    texto("## Estatística descritiva\n\n"
          "Conferi a quantidade de valores, a média, o desvio padrão, "
          "o mínimo, os quartis e o máximo das colunas abaixo.\n\n"
          f"```text\n{estatisticas.to_string()}\n```")
    codigo(f"df[{list(estatisticas.columns)!r}].describe().round(2)")
    texto("## Gráficos\n\nOs gráficos abaixo foram gerados na mesma execução da análise.")
    for nome in ["faturamento_por_filial.png", "faturamento_por_produto.png",
                 "formas_de_pagamento.png", "vendas_por_dia_semana.png"]:
        imagem = base64.b64encode((GRAFICOS_DIR / nome).read_bytes()).decode("ascii")
        celulas.append({"cell_type": "markdown", "metadata": {},
                        "source": f"![Gráfico de vendas](attachment:{nome})",
                        "attachments": {nome: {"image/png": imagem}}})
    texto("## Hipóteses exploratórias\n\n" + texto_hipoteses)

    notebook = {"cells": celulas, "nbformat": 4, "nbformat_minor": 4,
                "metadata": {"kernelspec": {"display_name": "Python 3",
                                           "language": "python", "name": "python3"},
                             "language_info": {"name": "python"}}}
    caminho = ESTATISTICAS_DIR / "analise_vendas.ipynb"
    caminho.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Notebook salvo em: {caminho}")


# 1) Leitura da Silver e criação do dia da semana em português.
engine = get_engine()
df = pd.read_sql_table("vendas_tratada", engine, schema="silver")
if df.empty:
    raise ValueError("A Silver está vazia. Execute primeiro o tratamento.")
df["data_venda"] = pd.to_datetime(df["data_venda"])
df["dia_semana"] = df["data_venda"].dt.day_name().map(DIAS_SEMANA_PT)
print(f"Vendas lidas da Silver: {len(df)}")

# 2) Resumos que serão usados nas respostas, nos arquivos e na Gold.
vendas_por_filial = df.groupby("filial").agg(
    faturamento=("valor_total", "sum"), qtd_vendas=("id_venda", "count"))
vendas_por_filial["ticket_medio"] = (
    vendas_por_filial["faturamento"] / vendas_por_filial["qtd_vendas"]).round(2)
vendas_por_linha = df.groupby("linha_produto").agg(
    faturamento=("valor_total", "sum"), avaliacao_media=("avaliacao", "mean"),
    qtd_vendas=("id_venda", "count"))
contagem_pagamento = df["forma_pagamento"].value_counts()
contagem_dias = df["dia_semana"].value_counts()
resumo_pagamentos = pd.DataFrame({
    "forma_pagamento": contagem_pagamento.index,
    "qtd_vendas": contagem_pagamento.values,
    "percentual": (100 * contagem_pagamento.values / len(df)).round(2),
})

# Identifica os maiores resultados de cada indicador.
filial_faturamento = vendas_por_filial["faturamento"].idxmax()
filial_quantidade = vendas_por_filial["qtd_vendas"].idxmax()
produto_faturamento = vendas_por_linha["faturamento"].idxmax()
if vendas_por_linha["avaliacao_media"].notna().any():
    produto_avaliacao = vendas_por_linha["avaliacao_media"].idxmax()
    nota = numero_br(vendas_por_linha.loc[produto_avaliacao, "avaliacao_media"])
    resposta_avaliacao = f"{produto_avaliacao} (nota média {nota})"
else:
    produto_avaliacao = None
    resposta_avaliacao = "Não há avaliações disponíveis na base."
pagamento = contagem_pagamento.idxmax()
dia = contagem_dias.idxmax()
valor_medio = df["valor_total"].mean()
maior_venda = df.loc[df["valor_total"].idxmax()]

# 3) Respostas às oito perguntas de negócio.
respostas = [
    f"1) Filial com maior faturamento: {filial_faturamento} "
    f"({numero_br(vendas_por_filial.loc[filial_faturamento, 'faturamento'])})",
    f"2) Filial com mais vendas: {filial_quantidade} "
    f"({vendas_por_filial.loc[filial_quantidade, 'qtd_vendas']} vendas)",
    f"3) Linha com maior faturamento: {produto_faturamento} "
    f"({numero_br(vendas_por_linha.loc[produto_faturamento, 'faturamento'])})",
    f"4) Linha com melhor avaliação média: {resposta_avaliacao}",
    f"5) Pagamento mais utilizado: {pagamento} ({contagem_pagamento.max()} vendas)",
    f"6) Valor médio das vendas: {numero_br(valor_medio)}",
    f"7) Maior venda: {numero_br(maior_venda['valor_total'])} "
    f"(id={maior_venda['id_venda']}, filial={maior_venda['filial']}, "
    f"linha={maior_venda['linha_produto']})",
    f"8) Dia com mais vendas: {dia} ({contagem_dias.max()} vendas)",
]

# Hipóteses exploratórias: compara os resultados desta base, sem afirmar causalidade.
hipotese1 = "Confirmada" if filial_faturamento == filial_quantidade else "Não confirmada"
if produto_avaliacao is None:
    hipotese2 = "Não foi possível avaliar: não há avaliações."
else:
    hipotese2 = "Confirmada" if produto_faturamento == produto_avaliacao else "Não confirmada"
texto_respostas = (
    "PERGUNTAS DE NEGÓCIO — SUPERMARKET SALES\n"
    "Valores na unidade monetária da base, sem conversão.\n\n"
    + "\n".join(respostas)
    + "\n\nHIPÓTESES EXPLORATÓRIAS\n"
    + f"H1: A filial com mais vendas também tem o maior faturamento. {hipotese1}.\n"
    + f"H2: A linha com maior faturamento também tem a melhor avaliação. {hipotese2}.\n"
    + "Conclusões limitadas ao período da base; não demonstram causa e efeito.\n"
)
print("\n" + texto_respostas)

# 4) Estatística descritiva e salvamento dos arquivos.
colunas_numericas = ["preco_unitario", "quantidade", "valor_total", "custo_mercadoria", "avaliacao"]
estatisticas = df[colunas_numericas].describe().round(2)
print(estatisticas)
estatisticas.to_csv(ESTATISTICAS_DIR / "estatisticas_descritivas.csv")
vendas_por_filial.to_csv(ESTATISTICAS_DIR / "resumo_filiais.csv")
resumo_pagamentos.to_csv(ESTATISTICAS_DIR / "resumo_pagamentos.csv", index=False)
vendas_por_linha[["faturamento", "avaliacao_media"]].to_csv(
    ESTATISTICAS_DIR / "resumo_produtos.csv")

# 5) Quatro gráficos para apoiar a leitura dos resultados.
ax = vendas_por_filial["faturamento"].sort_values(ascending=False).plot(
    kind="bar", figsize=(7, 5), color="#4C72B0")
salvar_grafico(ax, "Faturamento por filial", "faturamento_por_filial.png",
               "Filial", "Faturamento (unidade da base)")
ax = vendas_por_linha["faturamento"].sort_values().plot(
    kind="barh", figsize=(8, 5), color="#55A868")
salvar_grafico(ax, "Faturamento por linha de produto", "faturamento_por_produto.png",
               "Faturamento (unidade da base)", "Linha de produto")
ax = contagem_pagamento.plot(kind="pie", figsize=(6, 6), autopct="%1.1f%%")
salvar_grafico(ax, "Formas de pagamento", "formas_de_pagamento.png", "", "")
ordem_dias = list(DIAS_SEMANA_PT.values())
ax = contagem_dias.reindex(ordem_dias, fill_value=0).plot(
    kind="bar", figsize=(8, 5), color="#8172B2")
salvar_grafico(ax, "Vendas por dia da semana", "vendas_por_dia_semana.png",
               "Dia da semana", "Quantidade de vendas")

# 6) Reaproveita os resumos para preencher as cinco tabelas Gold existentes.
tabelas_gold = {
    "indicadores_filial": vendas_por_filial.rename(
        columns={"faturamento": "faturamento_total"}).reset_index(),
    "indicadores_linha_produto": vendas_por_linha.rename(
        columns={"faturamento": "faturamento_total"}).round(2).reset_index(),
    "indicadores_forma_pagamento": resumo_pagamentos,
    "indicadores_dia_semana": contagem_dias.rename_axis("dia_semana").reset_index(name="qtd_vendas"),
    "resumo_geral": pd.DataFrame([{
        "valor_medio_venda": round(valor_medio, 2),
        "maior_venda_valor": round(maior_venda["valor_total"], 2),
        "maior_venda_id": maior_venda["id_venda"],
        "maior_venda_filial": maior_venda["filial"],
        "maior_venda_linha_produto": maior_venda["linha_produto"],
    }]),
}
# Se alguma inserção falhar, a transação desfaz todas as mudanças na Gold.
with engine.begin() as conn:
    for nome, tabela in tabelas_gold.items():
        conn.execute(text(f"TRUNCATE TABLE gold.{nome}"))
        tabela.to_sql(nome, conn, schema="gold", if_exists="append", index=False)
print(f"Estatísticas salvas em: {ESTATISTICAS_DIR}")
print(f"Quatro gráficos salvos em: {GRAFICOS_DIR}")
print("Cinco tabelas da Gold atualizadas com sucesso.")

# 7) Gera o notebook depois de concluir os resultados e a carga Gold.
texto_hipoteses = (
    f"**H1:** A filial com mais vendas também tem o maior faturamento. {hipotese1}.\n\n"
    f"Comparei {filial_quantidade}, que teve mais vendas, com {filial_faturamento}, "
    "que teve o maior faturamento.\n\n"
    f"**H2:** A linha com maior faturamento também tem a melhor avaliação. {hipotese2}.\n\n"
    f"A linha com maior faturamento foi {produto_faturamento}. "
    f"A melhor avaliação média foi: {resposta_avaliacao}\n\n"
    "Essas conclusões valem para o período da base e não demonstram causa e efeito."
)
salvar_notebook(respostas, texto_hipoteses, estatisticas)
