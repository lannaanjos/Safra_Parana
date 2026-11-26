import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter
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
from Solver.config import EMPRESARIAL, FAMILIAR, MUNICIPIOS, ORC_PAA, RAIZ, SOCIOBIO

# FORMATAÇÃO (padrão brasileiro: 1.234.567,89)
def brl(valor: float, casas: int = 0) -> str:
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _nome(produto: str) -> str:
    return (produto.title().replace("Cafe", "Café").replace("Feijao", "Feijão")
            .replace("Pinhao", "Pinhão").replace(" De ", " de "))


def _dinheiro(v: float) -> str:
    if abs(v) >= 1e9:
        return f"R$ {brl(v / 1e9, 2)} bi"
    if abs(v) >= 1e6:
        return f"R$ {brl(v / 1e6, 1)} mi"
    return f"R$ {brl(v / 1e3, 0)} mil"


# GRÁFICO (4 painéis: lucro por ha, área, lucro total e uso das restrições)
def grafico(res: dict, dados: dict) -> None:
    t = res["tabela"].copy()
    t["rotulo"] = t["municipio"] + " · " + t["produto"].map(_nome)
    t.loc[t["safra"] != "TODAS", "rotulo"] += " (" + t["safra"].str.title() + ")"
    cor_cat = {EMPRESARIAL: "#3B7DD8", FAMILIAR: "#E8913A", SOCIOBIO: "#4BA36B"}
    nome_cat = {EMPRESARIAL: "Empresarial", FAMILIAR: "Familiar", SOCIOBIO: "Sociobiodiversidade"}
    milhar = FuncFormatter(lambda v, _: brl(v))

    fig, ax = plt.subplots(2, 2, figsize=(17, 10.5))
    fig.suptitle(f"Safra Paraná: lucro total ótimo de R$ {brl(res['Z'] / 1e9, 2)} bilhões",
                 fontsize=16, fontweight="bold")

    # A) lucro por hectare de cada combinação
    a = ax[0, 0]
    d = t.sort_values("lucro_ha")
    cores = ["#D9534F" if v < 0 else ("#4BA36B" if m > 0 else "#B0B7BF")
             for v, m in zip(d["lucro_ha"], d["modulos"])]
    a.barh(d["rotulo"], d["lucro_ha"], color=cores)
    for y, v in enumerate(d["lucro_ha"]):
        a.text(v, y, " " + brl(v) if v >= 0 else brl(v) + " ", va="center",
               ha="left" if v >= 0 else "right", fontsize=7)
    a.axvline(0, color="black", linewidth=0.8)
    a.set_title("A) Lucro por hectare de cada combinação (R$/ha)")
    a.xaxis.set_major_formatter(milhar)
    a.margins(x=0.15)
    a.tick_params(axis="y", labelsize=8)
    a.legend(handles=[Patch(color="#4BA36B", label="plantado no ótimo"),
                      Patch(color="#B0B7BF", label="lucro positivo, não plantado"),
                      Patch(color="#D9534F", label="lucro negativo")],
             loc="lower right", fontsize=8)

    # B) área disponível x área plantada por município
    b = ax[0, 1]
    disp = pd.Series(dados["area_municipio"]).sort_values()
    plantado = t.groupby(["cod_ibge", "produto"])["area_ha"].sum().unstack(fill_value=0)
    plantado = plantado.loc[:, plantado.sum() > 0]
    plantado = plantado.reindex(disp.index, fill_value=0)
    nomes = [MUNICIPIOS[c] for c in disp.index]
    b.barh(nomes, disp.values, color="#E4E7EB", label="área de lavoura disponível")
    esquerda = pd.Series(0.0, index=disp.index)
    paleta = ["#4C72B0", "#DD8452", "#8172B3", "#937860", "#DA8BC3", "#8C8C8C"]  # sem vermelho/verde
    for i, prod in enumerate(plantado.columns):
        b.barh(nomes, plantado[prod].values, left=esquerda.values, color=paleta[i % len(paleta)],
               label=f"{_nome(prod)} plantado")
        esquerda += plantado[prod]
    b.set_title("B) Área de lavoura por município: disponível x plantada (ha)")
    b.xaxis.set_major_formatter(milhar)
    b.legend(loc="lower right", fontsize=8)

    # C) lucro total das combinações plantadas
    c = ax[1, 0]
    p = t[t["modulos"] > 0].sort_values("lucro_total")
    c.barh(p["rotulo"], p["lucro_total"], color=[cor_cat[e] for e in p["empreendimento"]])
    for y, v in enumerate(p["lucro_total"]):
        c.text(v, y, " " + _dinheiro(v), va="center", fontsize=9)
    c.set_title("C) Lucro total do que o modelo planta")
    c.xaxis.set_major_formatter(FuncFormatter(lambda v, _: brl(v / 1e6)))
    c.set_xlabel("R$ milhões")
    c.margins(x=0.2)
    c.legend(handles=[Patch(color=cor_cat[e], label=nome_cat[e])
                      for e in cor_cat if e in set(p["empreendimento"])],
             loc="lower right", fontsize=8)

    # D) uso das restrições (as que chegam perto de 100% seguram o ótimo)
    dd = ax[1, 1]
    u = res["restricoes"].query("uso_pct > 0.05").sort_values("uso_pct")
    dd.barh(u["restricao"], u["uso_pct"],
            color=["#D9534F" if v >= 99 else "#7A8CA3" for v in u["uso_pct"]])
    for y, v in enumerate(u["uso_pct"]):
        dd.text(v, y, f" {brl(v, 1)}%", va="center", fontsize=8)
    dd.axvline(100, color="black", linestyle="--", linewidth=0.8)
    dd.set_xlim(0, 112)
    dd.set_title("D) Uso das restrições (vermelho = no limite, segura o ótimo)")
    dd.tick_params(axis="y", labelsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    caminho = RAIZ / "resultado.png"
    fig.savefig(caminho, dpi=150)
    print(f"\ngráfico salvo em {caminho}")
    plt.show()


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

    grafico(res, dados)


if __name__ == "__main__":
    main()

# A FAZER AINDA:
# - soja: 12º lev de 2024/25 cai de 5,86 para 5,34 mi ha, tem q ver se usa o 11º
# - teto nacional: hoje é consumo + exportação 2024/25, todos concordam?
# - custos: média desde 2023 (antes disso o triticale some)
# - preços: média de 2024 e 2025, trigo e mandioca ponderados (descrito no README)
# - N_MODULOS ainda provisório, tem q calcular