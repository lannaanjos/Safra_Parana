import pandas as pd
import os

pasta = "./dados"

custos = pd.read_csv("./dados/custo_producao.csv")
precos = pd.read_csv("./dados/preco_mensal_uf.csv")
armazens = pd.read_csv("./dados/armazens_cadastrados.csv")
cafe = pd.read_csv("./dados/armazens_cadastrados.csv")
graos = pd.read_csv("./dados/armazens_cadastrados.csv")

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
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".csv"):
            caminho = os.path.join(pasta, arquivo)

            df = pd.read_csv(caminho)

            print(f"\nArquivo: {arquivo}")
            print(df.columns.tolist())
            print(df.head())

    


