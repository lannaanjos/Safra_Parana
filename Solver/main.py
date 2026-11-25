import pulp
import dados


N_MODULOS = 1000

AREA = {}
for c, v in dados.area_lavoura().items():
    AREA[dados.MUNICIPIOS[c]] = v

ARM_E = {}
for c, v in dados.armazenagem().items():
    ARM_E[dados.MUNICIPIOS[c]] = v

    

TAM = sum(AREA.values()) / N_MODULOS

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

    # PARÂMETROS (falta fazer): Lucro(k), K(m), K(c), Kfam, Karm, Tam
    # MODELO (falta fazer): PuLP


if __name__ == "__main__":
    main()

# A FAZER AINDA:
# - soja: 12º lev de 2024/25 cai de 5,86 para 5,34 mi ha, tem q ver se usa o 11º
# - teto nacional: hoje é consumo + exportação 2024/25, todos concordam?
# - custos: média desde 2023 (antes disso o triticale some)
# - preços: média de 2024 e 2025, trigo e mandioca ponderados (descrito no README)
# - N_MODULOS ainda provisório, tem q calcular