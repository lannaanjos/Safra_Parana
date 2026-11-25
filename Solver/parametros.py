import pandas as pd

from Solver.config import (
    CULTURA_POR_PRODUTO,
    CULTURAS_TETO_NACIONAL,
    FAMILIAR,
    PRODUTOS_ARMAZENAVEIS,
    TAM,
)

def _chave_area(produto: str, safra: str) -> tuple[str, str]:
    # descobre a qual limite de área estadual uma combinação pertence
    # os limites estão em dados["area_estadual"], com chave (cultura, safra)
    
    cultura = CULTURA_POR_PRODUTO[produto]
    return (cultura, safra if cultura == "MILHO" else "TODAS")

def montar_parametros(dados: dict) -> dict:
    # junta custo e preço e calcula o lucro por hectare
    df = dados["custos"].merge(dados["precos"], on="produto", how="left")

    df["receita_ha"] = df["prod_kg_ha"] * df["preco_kg"]
    df["lucro_ha"] = df["receita_ha"] - df["custo_total_ha"]

    # cada linha do df é uma combinação
    K = list(df.index)
    Lucro = df["lucro_ha"].to_dict()
    Prod = df["prod_kg_ha"].to_dict()
    Preco = df["preco_kg"].to_dict()

    # conjuntos
    K_m = {cod: [] for cod in dados["area_municipio"]}
    K_area = {chave: [] for chave in dados["area_estadual"]} # (cultura, safra)
    K_teto = {cultura: [] for cultura in dados["teto_nacional"]} # cultura 
    K_fam, K_arm = [], []


    for k, linha in df.iterrows():
        K_m[linha["cod_ibge"]].append(k)

        if linha["empreendimento"] == FAMILIAR:
            K_fam.append(k)

        if linha["produto"] in PRODUTOS_ARMAZENAVEIS:
            K_arm.append(k)

            chave = _chave_area(linha["produto"], linha["safra"])
            K_area[chave].append(k)

            cultura = CULTURA_POR_PRODUTO[linha["produto"]]
            if cultura in K_teto: # só soja, milho, feijão e trigo
                K_teto[cultura].append(k)

    # máximo de módulos inteiros que cabem em cada município
    modulos_max = {}
    for cod, area in dados["area_municipio"].items():
        modulos_max[cod] = int(area // TAM)


    return {
    "tabela": df, "K": K, "Tam": TAM,
    "Lucro": Lucro, "Prod": Prod, "Preco": Preco,
    "K_m": K_m, "K_area": K_area, "K_teto": K_teto,
    "K_fam": K_fam, "K_arm": K_arm,
    "modulos_max": modulos_max,
    }

