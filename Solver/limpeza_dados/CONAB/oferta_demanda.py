from Solver.config import CSV_OFERTA, CULTURAS_TETO_NACIONAL, SAFRA_OFERTA
from Solver.limpeza_dados.limpeza_dados import carregar_csv

KG_POR_MIL_T = 1_000_000


def limpar_oferta_demanda() -> dict[str, float]:
    # teto de mercado nacional (kg) por cultura: TetoNac(c)
    # teto = consumo interno + exportação (demanda total pelo produto brasileiro)
    # calculado pelo balanço (estoque inicial + produção + importação - estoque final),
    # porque a coluna consumo_1000t da soja não fecha com o balanço do próprio CSV
    df = carregar_csv(CSV_OFERTA)
    df = df[(df["produto"].isin(CULTURAS_TETO_NACIONAL)) & (df["dsc_safra"] == SAFRA_OFERTA)]

    faltando = CULTURAS_TETO_NACIONAL - set(df["produto"])
    if faltando:
        raise ValueError(f"Culturas sem oferta/demanda em {SAFRA_OFERTA}: {sorted(faltando)}")

    demanda = (
        df["estoque_inicial_1000t"]
        + df["producao_1000t"]
        + df["importacao_1000t"]
        - df["estoque_final_1000t"]
    ) * KG_POR_MIL_T
    return dict(zip(df["produto"], demanda))