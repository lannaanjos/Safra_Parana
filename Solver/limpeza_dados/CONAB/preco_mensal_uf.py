import pandas as pd

from Solver.config import CSV_PRECOS, MAPA_PRECOS, NIVEL_PRECO, UF
from Solver.limpeza_dados.limpeza_dados import carregar_csv


def _mapa_para_tabela() -> pd.DataFrame:
    linhas = [
        (produto_custo, produto_preco, classificacao, peso)
        for produto_custo, itens in MAPA_PRECOS.items()
        for produto_preco, classificacao, peso in itens
    ]
    return pd.DataFrame(
        linhas, columns=["produto", "produto_preco", "classificao_produto", "peso"]
    )


def _precos_medios_pr() -> pd.DataFrame:
    df = carregar_csv(CSV_PRECOS)
    df = df[(df["uf"] == UF) & (df["dsc_nivel_comercializacao"] == NIVEL_PRECO)]
    return (
        df.groupby(["produto", "classificao_produto"], as_index=False)["valor_produto_kg"]
        .mean()
        .rename(columns={"produto": "produto_preco"})
    )


def _validar(df: pd.DataFrame) -> None:
    faltando = set(MAPA_PRECOS) - set(df["produto"])
    if faltando:
        raise ValueError(f"Produtos sem preço: {sorted(faltando)}")


def limpar_precos() -> pd.DataFrame:
    # preço médio recebido pelo produtor no PR (R$/kg)
    # o valor é ponderado pelas classificações
    mapa = _mapa_para_tabela()
    precos = _precos_medios_pr()
    df = mapa.merge(precos, on=["produto_preco", "classificao_produto"], how="inner")
    df["valor_ponderado"] = df["valor_produto_kg"] * df["peso"]
    resultado = df.groupby("produto", as_index=False)[["valor_ponderado", "peso"]].sum()
    resultado["preco_kg"] = resultado["valor_ponderado"] / resultado["peso"]
    resultado = resultado[["produto", "preco_kg"]]
    _validar(resultado)
    return resultado