from Solver.config import CSV_CAFE, UF, ULTIMO_LEV_CAFE
from Solver.limpeza_dados.limpeza_dados import carregar_csv


def limpar_cafe() -> dict[tuple[str, str], float]:
    # área plantada de café no PR (ha)
    # último levantamento do ano completo mais recente.
    # a coluna area_plantada_mil_ha já vem em hectares apesar do nome
    df = carregar_csv(CSV_CAFE)
    df = df[(df["uf"] == UF) & (df["id_levantamento"] == ULTIMO_LEV_CAFE)]
    if df.empty:
        raise ValueError("Nenhum levantamento completo de café no PR.")
    linha = df.loc[df["ano_agricola"].idxmax()]
    return {("CAFE", "TODAS"): float(linha["area_plantada_mil_ha"])}