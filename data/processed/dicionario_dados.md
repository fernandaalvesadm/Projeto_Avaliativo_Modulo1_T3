# Dicionário de Dados

Este dicionário explica o que significa cada coluna da base tratada do projeto Supermarket Sales.

Os dados tratados ficam na tabela `silver.vendas_tratada` e no arquivo `data/processed/vendas_tratadas.csv`.

## Colunas da base tratada

A tabela abaixo mostra o nome de cada coluna, o tipo usado no banco e as regras definidas para os dados.

| Coluna | Tipo no banco | O que significa | Regra no banco |
| --- | --- | --- | --- |
| id_venda | VARCHAR(50) | Código que identifica cada venda. | Não pode ser vazio nem repetido. |
| filial | VARCHAR(10) | Filial onde aconteceu a venda: Alex, Cairo ou Giza. | Não pode ser vazio. |
| cidade | VARCHAR(100) | Cidade da filial: Yangon, Naypyitaw ou Mandalay. | Não pode ser vazio. |
| tipo_cliente | VARCHAR(50) | Tipo de cliente: Member ou Normal. | Pode ser vazio. |
| genero | VARCHAR(20) | Gênero informado na base: Male ou Female. | Pode ser vazio. |
| linha_produto | VARCHAR(150) | Categoria do produto vendido. | Não pode ser vazio. |
| preco_unitario | NUMERIC(10,2) | Preço de uma unidade do produto. | Não pode ser negativo. |
| quantidade | INTEGER | Quantidade de unidades vendidas. | Deve ser maior que zero. |
| imposto | NUMERIC(10,2) | Valor informado na coluna Tax 5% da base original. | Não pode ser negativo. |
| valor_total | NUMERIC(12,2) | Valor total da venda, incluindo o imposto. | Não pode ser negativo. |
| data_venda | DATE | Data em que aconteceu a venda. | Sem restrição adicional. |
| hora_venda | TIME | Horário em que aconteceu a venda. | Sem restrição adicional. |
| forma_pagamento | VARCHAR(50) | Forma de pagamento: Cash, Credit card ou Ewallet. | Não pode ser vazio. |
| custo_mercadoria | NUMERIC(12,2) | Custo da mercadoria vendida. | Não pode ser negativo. |
| margem_percentual | NUMERIC(10,2) | Percentual de margem informado na base. | Sem restrição adicional. |
| receita_bruta | NUMERIC(12,2) | Valor registrado na coluna gross income da base original. | Não pode ser negativo. |
| avaliacao | NUMERIC(4,2) | Nota dada pelo cliente para a compra. | Deve estar entre 0 e 10. |

Essas regras são do banco. O Python também confere os dados antes de salvar, como datas válidas e valores necessários aos cálculos.

Os valores monetários foram mantidos como estão na base, sem conversão de moeda.

## Colunas criadas no tratamento

Também criei três colunas para ajudar na análise das vendas. Elas ficam no CSV tratado, mas não na tabela Silver.

| Coluna | Tipo | O que significa |
| --- | --- | --- |
| dia_semana | Texto | Dia da semana em que aconteceu a venda. No CSV, o nome está em inglês. |
| mes | Inteiro | Número do mês da venda, de 1 a 12. |
| periodo_dia | Texto | Manhã: antes das 12h; Tarde: das 12h até antes das 18h; Noite: a partir das 18h. |

Por isso, a tabela no banco tem 17 colunas e o CSV tratado tem 20. Nos resultados da análise, os dias da semana aparecem em português.

## Origem dos dados

Utilizei a base pública [Supermarket Sales, disponível no Kaggle](https://www.kaggle.com/datasets/faresashraf1001/supermarket-sales).

Na conferência do arquivo original, encontrei 1.000 vendas e 17 colunas. Não foram encontrados campos vazios ou vendas duplicadas, e as 1.000 vendas foram mantidas após o tratamento.