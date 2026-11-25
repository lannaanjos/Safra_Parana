from Solver.config import CSV_ARMAZENS, MUNICIPIOS
from Solver.limpeza_dados.limpeza_dados import carregar_csv

COLUNA_CAPACIDADE = "qtd_capacidade_estatica(t)"


def limpar_armazens() -> dict[int, float]:
    # capacidade estática total por município (t): ArmE(m)
    df = carregar_csv(CSV_ARMAZENS)
    df = df[df["cod_ibge"].isin(MUNICIPIOS)]
    capacidade = df.groupby("cod_ibge")[COLUNA_CAPACIDADE].sum().to_dict()

    faltando = set(MUNICIPIOS) - set(capacidade)
    if faltando:
        raise ValueError(f"Municípios sem armazém cadastrado: {sorted(faltando)}")
    return capacidade