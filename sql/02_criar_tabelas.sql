-- =============================================================================
-- 02_criar_tabelas.sql
-- Fase 0 - Criação dos esquemas e tabelas (Bronze, Silver, Gold)
-- =============================================================================
-- Execute este script já conectado ao banco "projeto_supermarket_sales".
--
-- Estrutura seguindo a Arquitetura Medallion:
--   bronze  -> Camada Raw (cópia fiel do CSV original)
--   silver  -> Camada Tratada (dados limpos, tipados e validados)
--   gold    -> Indicadores de negócio já agregados (perguntas da atividade)
--
-- O CSV tratado também inclui dia_semana, mes e periodo_dia.
-- Essas três colunas derivadas não são gravadas na tabela Silver.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- -----------------------------------------------------------------------------
-- BRONZE.RAW_VENDAS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS bronze.raw_vendas;

CREATE TABLE bronze.raw_vendas (
    invoice_id                  VARCHAR(50)     NOT NULL,
    branch                      VARCHAR(10),
    city                        VARCHAR(100),
    customer_type                VARCHAR(50),
    gender                       VARCHAR(20),
    product_line                 VARCHAR(150),
    unit_price                   NUMERIC(10,2),
    quantity                     INTEGER,
    tax_5_percent                 NUMERIC(10,4),
    sales                         NUMERIC(12,4),
    sale_date                    VARCHAR(20),
    sale_time                    VARCHAR(20),
    payment                       VARCHAR(50),
    cogs                          NUMERIC(12,4),
    gross_margin_percentage       NUMERIC(12,9),
    gross_income                  NUMERIC(12,4),
    rating                        NUMERIC(4,2),
    CONSTRAINT pk_raw_vendas PRIMARY KEY (invoice_id)
);

COMMENT ON TABLE bronze.raw_vendas IS
    'Camada Bronze/Raw: cópia fiel do CSV original, sem transformação de negócio.';

-- -----------------------------------------------------------------------------
-- SILVER.VENDAS_TRATADA
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS silver.vendas_tratada;

CREATE TABLE silver.vendas_tratada (
    id_venda             VARCHAR(50)     NOT NULL,
    filial               VARCHAR(10)     NOT NULL,
    cidade               VARCHAR(100)    NOT NULL,
    tipo_cliente         VARCHAR(50),
    genero               VARCHAR(20),
    linha_produto        VARCHAR(150)    NOT NULL,
    preco_unitario       NUMERIC(10,2)   CHECK (preco_unitario >= 0),
    quantidade           INTEGER         CHECK (quantidade > 0),
    imposto              NUMERIC(10,2)   CHECK (imposto >= 0),
    valor_total          NUMERIC(12,2)   CHECK (valor_total >= 0),
    data_venda           DATE,
    hora_venda           TIME,
    forma_pagamento      VARCHAR(50)     NOT NULL,
    custo_mercadoria     NUMERIC(12,2)   CHECK (custo_mercadoria >= 0),
    margem_percentual    NUMERIC(10,2),
    receita_bruta        NUMERIC(12,2)   CHECK (receita_bruta >= 0),
    avaliacao             NUMERIC(4,2)    CHECK (avaliacao BETWEEN 0 AND 10),
    CONSTRAINT pk_vendas_tratada PRIMARY KEY (id_venda)
);

COMMENT ON TABLE silver.vendas_tratada IS
    'Camada Silver/Tratada: dados limpos, tipados e validados.';

CREATE INDEX idx_vendas_tratada_filial ON silver.vendas_tratada (filial);
CREATE INDEX idx_vendas_tratada_linha_produto ON silver.vendas_tratada (linha_produto);
CREATE INDEX idx_vendas_tratada_data_venda ON silver.vendas_tratada (data_venda);

-- -----------------------------------------------------------------------------
-- GOLD (indicadores de negócio já agregados, recriados a cada execução)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS gold.indicadores_filial;
CREATE TABLE gold.indicadores_filial (
    filial              VARCHAR(10),
    qtd_vendas          INTEGER,
    faturamento_total   NUMERIC(14,2),
    ticket_medio        NUMERIC(12,2)
);
COMMENT ON TABLE gold.indicadores_filial IS
    'Gold: faturamento e quantidade de vendas por filial (perguntas 1 e 2).';

DROP TABLE IF EXISTS gold.indicadores_linha_produto;
CREATE TABLE gold.indicadores_linha_produto (
    linha_produto       VARCHAR(150),
    qtd_vendas          INTEGER,
    faturamento_total   NUMERIC(14,2),
    avaliacao_media     NUMERIC(4,2)
);
COMMENT ON TABLE gold.indicadores_linha_produto IS
    'Gold: faturamento e avaliação média por linha de produto (perguntas 3 e 4).';

DROP TABLE IF EXISTS gold.indicadores_forma_pagamento;
CREATE TABLE gold.indicadores_forma_pagamento (
    forma_pagamento     VARCHAR(50),
    qtd_vendas          INTEGER,
    percentual          NUMERIC(5,2)
);
COMMENT ON TABLE gold.indicadores_forma_pagamento IS
    'Gold: distribuição das formas de pagamento (pergunta 5).';

DROP TABLE IF EXISTS gold.indicadores_dia_semana;
CREATE TABLE gold.indicadores_dia_semana (
    dia_semana          VARCHAR(20),
    qtd_vendas          INTEGER
);
COMMENT ON TABLE gold.indicadores_dia_semana IS
    'Gold: quantidade de vendas por dia da semana (pergunta 8).';

DROP TABLE IF EXISTS gold.resumo_geral;
CREATE TABLE gold.resumo_geral (
    valor_medio_venda      NUMERIC(12,2),
    maior_venda_valor       NUMERIC(12,2),
    maior_venda_id          VARCHAR(50),
    maior_venda_filial      VARCHAR(10),
    maior_venda_linha_produto VARCHAR(150)
);
COMMENT ON TABLE gold.resumo_geral IS
    'Gold: valor médio das vendas e maior venda registrada (perguntas 6 e 7).';