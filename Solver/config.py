from pathlib import Path
import pandas as pd

PASTA_DADOS = Path(file).parent.parent / "Dados"
PASTA_CONAB = PASTA_DADOS / "Dataset_CONAB"

CSV_CUSTOS = PASTA_CONAB/"custo_producao.csv"
CSV_PRECOS = PASTA_CONAB/"preco_mensal_uf.csv"
CSV_ARMAZENS = PASTA_CONAB/"armazens_cadastrados.csv"
CSV_CAFE = PASTA_CONAB/"levantamento_cafe.csv"
CSV_GRAOS = PASTA_CONAB/"levantamento_graos.csv"