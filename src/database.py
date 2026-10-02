"""
database.py

Lê as configurações do arquivo .env e prepara o acesso ao PostgreSQL.
Os outros scripts usam a função get_engine() para acessar o banco.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL

# Localiza e lê o .env na pasta principal do projeto.
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def get_engine() -> Engine:
    """Confere as configurações e prepara o acesso ao banco."""
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    # Confere se alguma configuração obrigatória está vazia.
    faltando = [
        var
        for var, valor in [
            ("DB_HOST", host),
            ("DB_PORT", port),
            ("DB_NAME", name),
            ("DB_USER", user),
            ("DB_PASSWORD", password),
        ]
        if not valor
    ]

    if faltando:
        raise RuntimeError(
            "Configurações ausentes: "
            f"{', '.join(faltando)}. Copie o .env.example para .env "
            "e preencha os valores antes de executar o projeto."
        )

    # Monta a configuração de acesso ao PostgreSQL.
    url = URL.create(
        "postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=int(port),
        database=name,
    )

    return create_engine(url)