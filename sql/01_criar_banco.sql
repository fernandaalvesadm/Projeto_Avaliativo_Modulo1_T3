-- =============================================================================
-- 01_criar_banco.sql
-- Fase 0 - Criação do banco de dados do projeto
-- =============================================================================
-- Este script deve ser executado conectado ao banco padrão "postgres"
-- (não é possível criar um banco estando conectado a ele mesmo).
--
-- Conecte-se ao servidor PostgreSQL (banco "postgres") e execute este
-- script. Depois disso, abra uma nova conexão apontando para o banco
-- "projeto_supermarket_sales" para executar o restante dos scripts.
-- =============================================================================

CREATE DATABASE projeto_supermarket_sales
    WITH
    ENCODING = 'UTF8'
    TEMPLATE = template0;

COMMENT ON DATABASE projeto_supermarket_sales IS
    'Projeto - Análise de Dados com Python - Pipeline ETL Supermarket Sales';