from pathlib import Path

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

# CÓDIGO DO IBGE POR MUNICÍPIO
MUNICIPIOS = {
    4104501: "Capanema",
    4104808: "Cascavel",
    4106209: "Contenda",
    4107207: "Dois Vizinhos",
    4108403: "Francisco Beltrão",
    4109401: "Guarapuava",
    4113700: "Londrina",
    4119905: "Ponta Grossa",
    4120606: "Prudentópolis",
    4128104: "Umuarama",
}

UF = "PR"

# TIPOS
EMPRESARIAL = "AGRICULTURA EMPRESARIAL"
FAMILIAR = "AGRICULTURA FAMILIAR"
SOCIOBIO = "SOCIOBIODIVERSIDADE"

# CONSTANTES
N_MODULOS = 1000   # só para saber que precisa estar aqui, o valor correto ainda n foi calculado
ORC_PAA = 62_000_000
ANO_INICIO_CUSTOS = 2023

# 18 COMBINAÇÕES POSSÍVEIS
COMBINACOES = [
    (4119905, "SOJA", "TODAS", EMPRESARIAL),
    (4119905, "MILHO", "1ª SAFRA", EMPRESARIAL),
    (4119905, "FEIJAO COMUM CORES", "TODAS", EMPRESARIAL),
    (4119905, "TRIGO", "TODAS", EMPRESARIAL),
    (4119905, "TRITICALE", "TODAS", EMPRESARIAL),
    (4113700, "SOJA", "TODAS", EMPRESARIAL),
    (4113700, "MILHO", "2ª SAFRA", EMPRESARIAL),
    (4113700, "TRIGO", "TODAS", EMPRESARIAL),
    (4113700, "CAFE", "TODAS", FAMILIAR),
    (4104808, "TRIGO", "TODAS", EMPRESARIAL),
    (4104808, "MILHO", "2ª SAFRA", FAMILIAR),
    (4104501, "TRIGO", "TODAS", FAMILIAR),
    (4107207, "TRIGO", "TODAS", FAMILIAR),
    (4108403, "FEIJAO COMUM CORES", "TODAS", FAMILIAR),
    (4120606, "FEIJAO COMUM PRETO", "TODAS", FAMILIAR),
    (4106209, "BATATA", "TODAS", FAMILIAR),
    (4128104, "RAIZ DE MANDIOCA", "TODAS", FAMILIAR),
    (4109401, "PINHAO", "TODAS", SOCIOBIO),
]

# UNIDADES DE MEDIDA
KG_POR_UNIDADE = {"60 kg": 60, "25 kg": 25, "kg": 1, "t": 1000}

# PREÇOS
# produto do custo -> [(produto no CSV de preços, classificação, peso)]
# Pesos de trigo e mandioca conforme o README (trigo 72% PH 78 / 25% PH 75;
# mandioca 88% indústria / 12% mesa). Os pesos são normalizados no cálculo.
NIVEL_PRECO = "PREÇO RECEBIDO P/ PRODUTOR"
MAPA_PRECOS = {
    "SOJA": [("SOJA", "EM GRÃOS", 1)],
    "MILHO": [("MILHO", "EM GRÃOS", 1)],
    "FEIJAO COMUM CORES": [("FEIJAO", "COMUM CORES", 1)],
    "FEIJAO COMUM PRETO": [("FEIJAO", "COMUM PRETO", 1)],
    "TRIGO": [
        ("TRIGO", "PÃO, PH 78, TIPO 1", 0.72),
        ("TRIGO", "PÃO, PH 75, TIPO 2", 0.25),
    ],
    "TRITICALE": [("TRITICALE", "EM GRÃOS", 1)],
    "CAFE": [("CAFE", "ARÁBICA TIPO 6, BEBI", 1)],
    "BATATA": [("BATATA", "INGLESA", 1)],
    "RAIZ DE MANDIOCA": [
        ("RAIZ DE MANDIOCA", "INDÚSTRIA", 0.88),
        ("RAIZ DE MANDIOCA", "DE MESA", 0.12),
    ],
    "PINHAO": [("PINHAO", "IN NATURA", 1)],
}

# ARMAZENAGEM: produtos das combinações armazenáveis (Karm: grãos e café)
PRODUTOS_ARMAZENAVEIS = {
    "SOJA", "MILHO", "FEIJAO COMUM CORES", "FEIJAO COMUM PRETO",
    "TRIGO", "TRITICALE", "CAFE",
}

# ÁREA ESTADUAL (Ce) E TETO NACIONAL (Cn)
# produto do custo -> nome da cultura nos levantamentos e na oferta/demanda
CULTURA_POR_PRODUTO = {
    "SOJA": "SOJA",
    "MILHO": "MILHO",
    "FEIJAO COMUM CORES": "FEIJAO",
    "FEIJAO COMUM PRETO": "FEIJAO",
    "TRIGO": "TRIGO",
    "TRITICALE": "TRITICALE",
    "CAFE": "CAFE",
}
CULTURAS_GRAOS = {"SOJA", "MILHO", "FEIJAO", "TRIGO", "TRITICALE"}
CULTURAS_TETO_NACIONAL = {"SOJA", "MILHO", "FEIJAO", "TRIGO"}

# Último levantamento de um ano completo (grãos: 12; café: 4)
ULTIMO_LEV_GRAOS = 12
ULTIMO_LEV_CAFE = 4

# Safra da oferta e demanda (2025/26 ainda é projeção)
SAFRA_OFERTA = "2024/25"