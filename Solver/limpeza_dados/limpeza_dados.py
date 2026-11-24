import pandas as pd
from Solver.config import PASTA_CONAB


def remover_espacos(df: pd.DataFrame) -> pd.DataFrame:
    # tira espaços nas bordas dos nomes
    df = df.copy()
    df.columns = df.columns.str.strip()
    colunas_texto = df.select_dtypes(include=["object", "string"]).columns
    df[colunas_texto] = df[colunas_texto].apply(lambda col: col.str.strip())
    return df


def carregar_conab(nome_arquivo: str) -> pd.DataFrame:
    df = pd.read_csv(PASTA_CONAB / nome_arquivo)
    return remover_espacos(df)