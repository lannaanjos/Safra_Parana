import re
from pathlib import Path

import pandas as pd

# CAMINHOS DOS ARQUIVOS
RAIZ = Path(__file__).resolve().parent.parent

PASTA_DADOS = RAIZ / "Dados"
PASTA_CONAB = PASTA_DADOS / "Dataset_CONAB"
PASTA_IBGE = PASTA_DADOS / "IBGE"

CSV_CUSTOS = PASTA_CONAB / "custo_producao.csv"
CSV_PRECOS = PASTA_CONAB / "preco_mensal_uf.csv"
CSV_ARMAZENS = PASTA_CONAB / "armazens_cadastrados.csv"
CSV_CAFE = PASTA_CONAB / "levantamento_cafe.csv"
CSV_GRAOS = PASTA_CONAB / "levantamento_graos.csv"
CSV_OFERTA = PASTA_CONAB / "oferta_demanda.csv"
CSV_IBGE_AREA = PASTA_IBGE / "tabela5457.csv"


# LEITURA

def _ler(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho)
    df.columns = df.columns.str.strip()
    colunas_texto = df.select_dtypes(include=["object", "string"]).columns
    df[colunas_texto] = df[colunas_texto].apply(lambda col: col.str.strip())
    return df


# ESCOLHAS DO MODELO (não vêm de CSV)
UF = "PR"
TAM = 1
ORC_PAA = 62_000_000  
SAFRA_OFERTA = "2024/25"  
NIVEL_PRECO = "PREÇO RECEBIDO P/ PRODUTOR"


EMPRESARIAL = "AGRICULTURA EMPRESARIAL"
FAMILIAR = "AGRICULTURA FAMILIAR"
SOCIOBIO = "SOCIOBIODIVERSIDADE"

PESOS_CLASSIFICACAO = {
    "TRIGO": {"PÃO, PH 78, TIPO 1": 0.72, "PÃO, PH 75, TIPO 2": 0.25},
    "RAIZ DE MANDIOCA": {"INDÚSTRIA": 0.88, "DE MESA": 0.12},
}


# CUSTOS -> municípios, combinações, janela de anos e unidades
_CHAVE = ["cod_ibge", "produto", "safra", "empreendimento"]
_custos_uf = _ler(CSV_CUSTOS).query("uf == @UF")

# CÓDIGO DO IBGE POR MUNICÍPIO ("CAPANEMA-PR" -> "Capanema")
MUNICIPIOS = (
    _custos_uf[["cod_ibge", "municipio"]]
    .drop_duplicates("cod_ibge")
    .sort_values("cod_ibge")
    .assign(municipio=lambda d: d["municipio"].str.replace(f"-{UF}$", "", regex=True).str.title())
    .set_index("cod_ibge")["municipio"]
    .to_dict()
)

# COMBINAÇÕES (município, produto, safra, empreendimento) com custo no UF
COMBINACOES = sorted(

    _custos_uf[_CHAVE].drop_duplicates().itertuples(index=False, name=None)

)

# Primeiro ano em que todas as combinações ainda têm custo
# (o último ano do triticale limita: 2023)
ANO_INICIO_CUSTOS = int(_custos_uf.groupby(_CHAVE)["ano"].max().min())


# UNIDADES DE MEDIDA: "60 kg" -> 60, "kg" -> 1, "t" -> 1000
def _kg_da_unidade(texto: str) -> float:
    m = re.fullmatch(r"(?:(\d+(?:[.,]\d+)?)\s*)?(kg|t)", texto.strip().lower())
    if m is None:
        raise ValueError(f"Unidade de comercialização não reconhecida: {texto!r}")
    quantidade = float(m.group(1).replace(",", ".")) if m.group(1) else 1
    return quantidade * (1000 if m.group(2) == "t" else 1)


KG_POR_UNIDADE = {
    u: _kg_da_unidade(u) for u in sorted(_custos_uf["unidade_comercializacao"].unique())
}


_graos = _ler(CSV_GRAOS)
_cafe = _ler(CSV_CAFE)
_oferta = _ler(CSV_OFERTA)


def _ultimo_levantamento(df: pd.DataFrame) -> int:
    
    numerados = df[df["dsc_levantamento"].str.match(r"^\d+º\s*LEV")]
    return int(numerados["id_levantamento"].max())


# Último levantamento de um ano completo (grãos: 12; café: 4)

ULTIMO_LEV_GRAOS = _ultimo_levantamento(_graos)

ULTIMO_LEV_CAFE = _ultimo_levantamento(_cafe)


def _cultura_do_produto(produto: str, culturas: set[str]) -> str | None:
    # "FEIJAO COMUM CORES" -> "FEIJAO"; "PINHAO" não tem levantamento -> None
    candidatas = [c for c in culturas if produto == c or produto.startswith(c + " ")]
    return max(candidatas, key=len) if candidatas else None


_culturas_levantadas = set(_graos["produto"]) | set(_cafe["produto"])
_produtos = {c[1] for c in COMBINACOES}

# ÁREA ESTADUAL (Ce) E TETO NACIONAL (Cn)
# produto do custo -> nome da cultura nos levantamentos e na oferta/demanda
CULTURA_POR_PRODUTO = {
    p: c
    for p in sorted(_produtos)
    if (c := _cultura_do_produto(p, _culturas_levantadas)) is not None
}
CULTURAS_GRAOS = set(CULTURA_POR_PRODUTO.values()) & set(_graos["produto"])
CULTURAS_TETO_NACIONAL = CULTURAS_GRAOS & set(_oferta["produto"])

# ARMAZENAGEM: produtos das combinações armazenáveis (Karm: grãos e café)
PRODUTOS_ARMAZENAVEIS = set(CULTURA_POR_PRODUTO)


# PREÇOS
# produto do custo -> [(produto no CSV de preços, classificação, peso)]
_precos_uf = _ler(CSV_PRECOS).query(
    "uf == @UF and dsc_nivel_comercializacao == @NIVEL_PRECO"
)


def _itens_de_preco(produto: str) -> list[tuple[str, str, float]]:
    if produto in PESOS_CLASSIFICACAO:
        return [(produto, cls, peso) for cls, peso in PESOS_CLASSIFICACAO[produto].items()]

    nomes = set(_precos_uf["produto"])
    base = _cultura_do_produto(produto, nomes)
    if base is None:
        raise ValueError(f"Produto sem preço em {UF}: {produto!r}")

    classificacoes = set(_precos_uf.loc[_precos_uf["produto"] == base, "classificao_produto"])
    resto = produto[len(base):].strip()  # "FEIJAO COMUM PRETO" -> "COMUM PRETO"
    if resto in classificacoes:
        return [(base, resto, 1)]
    if len(classificacoes) == 1:
        return [(base, next(iter(classificacoes)), 1)]
    raise ValueError(
        f"{produto!r} tem várias classificações de preço {sorted(classificacoes)}; "
        "defina os pesos em PESOS_CLASSIFICACAO."
    )


MAPA_PRECOS = {p: _itens_de_preco(p) for p in sorted(_produtos)}