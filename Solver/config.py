from pathlib import Path
import pandas as pd

PASTA_DADOS = Path(file).parent.parent / "Dados"
PASTA_CONAB = PASTA_DADOS / "Dataset_CONAB"

CSV_CUSTOS = PASTA_CONAB/"custo_producao.csv"
CSV_PRECOS = PASTA_CONAB/"preco_mensal_uf.csv"
CSV_ARMAZENS = PASTA_CONAB/"armazens_cadastrados.csv"
CSV_CAFE = PASTA_CONAB/"levantamento_cafe.csv"
CSV_GRAOS = PASTA_CONAB/"levantamento_graos.csv"

N_MODULOS = 1000          
ORC_PAA = 62_000_000 

MUNICIPIOS = {
    4104501: "Capanema", 4104808: "Cascavel", 4106209: "Contenda",
    4107207: "Dois Vizinhos", 4108403: "Francisco Beltrão",
    4109401: "Guarapuava", 4113700: "Londrina", 4119905: "Ponta Grossa",
    4120606: "Prudentópolis", 4128104: "Umuarama",
}

