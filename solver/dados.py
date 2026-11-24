import pandas as pd
import os
from pathlib import Path

pasta_dados = Path(__file__).parent.parent / "Dados"
pasta_conab = pasta_dados / "Dataset_CONAB"

custos = pd.read_csv(pasta_conab/"custo_producao.csv")
precos = pd.read_csv(pasta_conab/"preco_mensal_uf.csv")
armazens = pd.read_csv(pasta_conab/"armazens_cadastrados.csv")
cafe = pd.read_csv(pasta_conab/"levantamento_cafe.csv")
graos = pd.read_csv(pasta_conab/"levantamento_graos.csv")

combinacoes_validas = [
    ("Ponta Grossa", "soja"),
    ("Ponta Grossa", "milho 1ª safra"),
    ("Ponta Grossa", "feijão cores"),
    ("Ponta Grossa", "trigo"),
    ("Ponta Grossa", "triticale"),
    ("Londrina", "soja"),
    ("Londrina", "milho 2ª safra"),
    ("Londrina", "trigo"),
    ("Londrina", "café"),
    ("Cascavel", "trigo"),
    ("Cascavel", "milho 2ª safra"),
    ("Capanema", "trigo"),
    ("Dois Vizinhos", "trigo"),
    ("Francisco Beltrão", "feijão cores"),
    ("Prudentópolis", "feijão preto"),
    ("Contenda", "batata"),
    ("Umuarama", "mandioca"),
    ("Guarapuava", "pinhão")
]

def extrair_dados():
    for arquivo in os.listdir(pasta_dados):
        if arquivo.endswith(".csv"):
            caminho = os.path.join(pasta_dados, arquivo)

            df = pd.read_csv(caminho)

            print(f"\nArquivo: {arquivo}")
            print(df.columns.tolist())
            print(df.head())

def main():

    extrair_dados()

    
if "__name__" == "__main__":
    main()

