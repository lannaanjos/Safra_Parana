from Solver.config import CSV_IBGE_AREA, MUNICIPIOS
from Solver.limpeza_dados.limpeza_dados import carregar_csv

LINHAS_CABECALHO = 5
COLUNAS = ["nivel", "cod_ibge", "municipio", "area_ha", "unidade"]


def limpar_area_lavoura() -> dict[int, float]:
    # área de lavoura por município (ha) segundo a PAM 2025
    df = carregar_csv(
        CSV_IBGE_AREA,
        sep=";",
        skiprows=LINHAS_CABECALHO,
        header=None,
        names=COLUNAS,
        encoding="utf-8-sig",
        engine="python",
        on_bad_lines="skip",
        dtype=str,
    )
    df = df[df["nivel"] == "MU"]  # descarta o rodapé de notas e legendas
    df["cod_ibge"] = df["cod_ibge"].astype(int)
    df["area_ha"] = df["area_ha"].astype(float)

    area = df.set_index("cod_ibge")["area_ha"].to_dict()
    faltando = set(MUNICIPIOS) - set(area)
    if faltando:
        raise ValueError(f"Municípios sem área no IBGE: {sorted(faltando)}")
    return {cod: area[cod] for cod in MUNICIPIOS}