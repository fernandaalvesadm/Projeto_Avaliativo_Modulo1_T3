"""
run_etl.py

Executa as etapas do projeto em sequência:
1. Leitura, carga da Bronze e exportação da consulta (Fases 1 e 2).
2. Tratamento e carga da Silver (Fase 3).
3. Análise, gráficos e carga da Gold (Fase 4).

O banco e as tabelas devem ser criados antes, pelos scripts SQL (Fase 0).

Executar na pasta principal do projeto:
    python src/run_etl.py
"""

import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent

ETAPAS = [
    "01_leitura_dados.py",
    "02_etl_vendas.py",
    "03_estatistica.py",
]


def main() -> None:
    for script in ETAPAS:
        print("\n" + "=" * 70)
        print(f"Executando: {script}")
        print("=" * 70)
        resultado = subprocess.run([sys.executable, str(SRC_DIR / script)], cwd=SRC_DIR)
        if resultado.returncode != 0:
            print(f"\nPipeline interrompido: {script} terminou com erro.")
            sys.exit(resultado.returncode)

    print("\nPipeline completo executado com sucesso.")


if __name__ == "__main__":
    main()