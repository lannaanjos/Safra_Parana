import pandas as pd

from Solver.config import CSV_GRAOS, CULTURAS_GRAOS, UF, ULTIMO_LEV_GRAOS
from Solver.limpeza_dados.limpeza_dados import carregar_csv

HA_POR_MIL_HA = 1000


def _ultimo_ano_completo(df: pd.DataFrame) -> pd.DataFrame:
    # último levantamento do ano agrícola completo mais recente
    # por cult e safra
    completos = df[df["id_levantamento"] == ULTIMO_LEV_GRAOS]
    ultimo_ano = completos.groupby(["produto", "safra"])["ano_agricola"].transform("max")
    return completos[completos["ano_agricola"] == ultimo_ano]


def _padronizar_safra(df: pd.DataFrame) -> pd.DataFrame:
    # miLho fica por safra
    # demais culturas somam todas as safras ("TODAS"),
    # como nas combinações do config
    df = df.copy()
    df["safra"] = df["safra"].where(df["produto"] == "MILHO", "TODAS")
    return df


def limpar_graos() -> dict[tuple[str, str], float]:
    # área plantada no PR (ha) por (cultura, safra): ÁreaEst(c) dos grãos
    df = carregar_csv(CSV_GRAOS)
    df = df[(df["uf"] == UF) & (df["produto"].isin(CULTURAS_GRAOS))]
    df = _ultimo_ano_completo(df)
    df = _padronizar_safra(df)
    area = df.groupby(["produto", "safra"])["area_plantada_mil_ha"].sum() * HA_POR_MIL_HA
    return area.to_dict()