import pandas as pd

from Solver.config import ANO_INICIO_CUSTOS, COMBINACOES, CSV_CUSTOS, KG_POR_UNIDADE
from Solver.limpeza_dados.limpeza_dados import carregar_csv

CHAVE = ["cod_ibge", "produto", "safra", "empreendimento"]


def _filtrar_combinacoes(df: pd.DataFrame) -> pd.DataFrame:
    combinacoes = pd.DataFrame(COMBINACOES, columns=CHAVE)
    return df.merge(combinacoes, on=CHAVE, how="inner")


def _calcular_por_hectare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kg_por_unidade = df["unidade_comercializacao"].map(KG_POR_UNIDADE)
    df["prod_kg_ha"] = (
        df["vlr_custo_variavel_ha"] / df["vlr_custo_variavel_unidade"] * kg_por_unidade
    )
    df["custo_total_ha"] = df["vlr_custo_variavel_ha"] + df["vlr_custo_fixo_ha"]
    return df


def _validar(df: pd.DataFrame) -> None:
    if len(df) != len(COMBINACOES):
        raise ValueError(f"Esperadas {len(COMBINACOES)} combinações, obtidas {len(df)}.")
    if df["prod_kg_ha"].isna().any():
        raise ValueError("Há unidade de comercialização fora de KG_POR_UNIDADE.")


def limpar_custos() -> pd.DataFrame:
    # custo total (R$/ha) e produtividade (kg/ha) médios por combinação
    df = carregar_csv(CSV_CUSTOS)
    df = df[df["ano"] >= ANO_INICIO_CUSTOS]
    df = _filtrar_combinacoes(df)
    df = _calcular_por_hectare(df)
    resultado = df.groupby(CHAVE, as_index=False)[["custo_total_ha", "prod_kg_ha"]].mean()
    _validar(resultado)
    return resultado