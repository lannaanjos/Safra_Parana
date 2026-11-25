import pandas as pd
# import dados

'''
N_MODULOS = 1000

AREA = {}
for c, v in dados.area_lavoura().items():
    AREA[dados.MUNICIPIOS[c]] = v

ARM_E = {}
for c, v in dados.armazenagem().items():
    ARM_E[dados.MUNICIPIOS[c]] = v

    

TAM = sum(AREA.values()) / N_MODULOS
'''

################ laNNA ##########
### não exclui o seu marcos mas add inicio da orquestração da limopeza here.
from Solver.limpeza_dados import (
    limpar_area_lavoura,
    limpar_armazens,
    limpar_cafe,
    limpar_custos,
    limpar_graos,
    limpar_oferta_demanda,
    limpar_precos,
)
from Solver.modelo import resolver
from Solver.parametros import montar_parametros
from Solver.config import ORC_PAA

# FORMATAÇÃO (padrão brasileiro: 1.234.567,89)
def brl(valor: float, casas: int = 0) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# LIMPEZA
def limpar_dados() -> dict:
    return {
        "custos": limpar_custos(), # custo/ha e Prod(k)
        "precos": limpar_precos(), # Preço(k) R$/kg
        "area_municipio": limpar_area_lavoura(), # Área(m) ha
        "armazenagem": limpar_armazens(), # ArmE(m) t
        "area_estadual": {**limpar_graos(), **limpar_cafe()}, # ÁreaEst(c) ha
        "teto_nacional": limpar_oferta_demanda(), # TetoNac(c) kg
    }


def main() -> None:
    dados = limpar_dados()

    for nome, valor in dados.items():
        print(f"{nome}: {len(valor)} registros")

    # K, TAM, Prod, Preco, K_m, K_area, K_teto, K_fam, K_arm e modulos_max
    par = montar_parametros(dados)
    print(par["tabela"][["cod_ibge", "produto", "prod_kg_ha", "preco_kg", "lucro_ha"]])

    # conjuntos
    K = par["K"]
    K_m = par["K_m"]
    K_area = par["K_area"]
    K_teto = par["K_teto"]
    K_fam = par["K_fam"]
    K_arm = par["K_arm"]

    # parametros por combinacaoo
    Tam = par["Tam"]
    Lucro = par["Lucro"]
    Prod = par["Prod"]
    Preco = par["Preco"]

    # parametros que vem de dados/config
    Area = dados["area_municipio"]
    ArmE = dados["armazenagem"]
    AreaEst = dados["area_estadual"]
    TetoNa = dados["teto_nacional"]
    OrcPAA = ORC_PAA 

    # MODELO
    res = resolver(par, dados, OrcPAA)

    print(f"\nstatus: {res['status']}")
    print(f"lucro total (Z): R$ {brl(res['Z'], 2)}  (R$ {brl(res['Z'] / 1e9, 2)} bilhões)")

    t = res["tabela"]
    plantado = t[t["modulos"] > 0].copy()
    plantado["area_ha"] = plantado["area_ha"].map(brl)
    plantado["lucro_total"] = plantado["lucro_total"].map(lambda v: "R$ " + brl(v))
    print("\nO que o modelo planta:")
    print(plantado[["municipio", "produto", "safra", "empreendimento",
                    "modulos", "area_ha", "lucro_total"]].to_string(index=False))

    cat = t.groupby("empreendimento")[["area_ha", "lucro_total"]].sum()
    cat["area_ha"] = cat["area_ha"].map(brl)
    cat["lucro_total"] = cat["lucro_total"].map(lambda v: "R$ " + brl(v))
    print("\nPor categoria de produtor:")
    print(cat)

    uso = res["restricoes"].copy()
    uso["uso"] = uso["uso"].map(brl)
    uso["limite"] = uso["limite"].map(brl)
    uso["uso_pct"] = uso["uso_pct"].map(lambda v: brl(v, 1) + "%")
    print("\nRestrições (uso / limite):")
    print(uso.to_string(index=False))


if __name__ == "__main__":
    main()

# A FAZER AINDA:
# - soja: 12º lev de 2024/25 cai de 5,86 para 5,34 mi ha, tem q ver se usa o 11º
# - teto nacional: hoje é consumo + exportação 2024/25, todos concordam?
# - custos: média desde 2023 (antes disso o triticale some)
# - preços: média de 2024 e 2025, trigo e mandioca ponderados (descrito no README)
# - N_MODULOS ainda provisório, tem q calcular