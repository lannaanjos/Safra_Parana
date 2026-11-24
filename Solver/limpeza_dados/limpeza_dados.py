from pathlib import Path
import pandas as pd


def remover_espacos(df: pd.DataFrame) -> pd.DataFrame:
    # tira espaços nas bordas dos nomes
    df = df.copy()
    df.columns = df.columns.str.strip()
    colunas_texto = df.select_dtypes(include=["object", "string"]).columns
    df[colunas_texto] = df[colunas_texto].apply(lambda col: col.str.strip())
    return df


def carregar_csv(caminho: Path, **kwargs) -> pd.DataFrame:
    # lê qualquer CSV e já devolve com os textos padronizados
    df = pd.read_csv(caminho, **kwargs)
    return remover_espacos(df)