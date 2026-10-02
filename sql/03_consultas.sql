-- =============================================================================
-- 03_consultas.sql
-- Fase 2 - Consultas de conferência dos dados brutos
-- =============================================================================
-- Execute cada consulta individualmente no DBeaver.
--
-- Para a etapa de exportação, salve o resultado da consulta 2 em:
-- data/raw/consulta_faturamento_por_filial.csv
-- =============================================================================

-- 1) Quantidade de vendas e período da base
-- A data está armazenada como texto no formato mês/dia/ano.
-- TO_DATE converte esse texto em data para comparar corretamente.
SELECT
    COUNT(*) AS total_vendas,
    MIN(TO_DATE(sale_date, 'MM/DD/YYYY')) AS data_inicial,
    MAX(TO_DATE(sale_date, 'MM/DD/YYYY')) AS data_final
FROM bronze.raw_vendas;


-- 2) Faturamento, quantidade de vendas e ticket médio por filial
-- Ticket médio é o valor médio de cada venda.
SELECT
    branch,
    COUNT(*) AS qtd_vendas,
    SUM(sales) AS faturamento_total,
    AVG(sales) AS ticket_medio
FROM bronze.raw_vendas
GROUP BY branch
ORDER BY faturamento_total DESC;


-- 3) Faturamento e avaliação média por linha de produto
SELECT
    product_line,
    COUNT(*) AS qtd_vendas,
    SUM(sales) AS faturamento_total,
    AVG(rating) AS avaliacao_media
FROM bronze.raw_vendas
GROUP BY product_line
ORDER BY faturamento_total DESC;


-- 4) Quantidade e percentual de vendas por forma de pagamento
SELECT
    payment,
    COUNT(*) AS qtd_vendas,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM bronze.raw_vendas),
        2
    ) AS percentual
FROM bronze.raw_vendas
GROUP BY payment
ORDER BY qtd_vendas DESC;


-- 5) Vendas com valor acima da média geral
SELECT
    invoice_id,
    branch,
    product_line,
    sales
FROM bronze.raw_vendas
WHERE sales > (
    SELECT AVG(sales)
    FROM bronze.raw_vendas
)
ORDER BY sales DESC;


-- 6) Maior venda registrada
SELECT *
FROM bronze.raw_vendas
ORDER BY sales DESC
LIMIT 1;


-- 7) Vendas por filial e forma de pagamento
SELECT
    branch,
    payment,
    COUNT(*) AS qtd_vendas,
    SUM(sales) AS faturamento_total
FROM bronze.raw_vendas
GROUP BY branch, payment
ORDER BY branch, faturamento_total DESC;