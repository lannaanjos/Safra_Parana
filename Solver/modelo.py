import math

import pandas as pd
import pulp

from Solver.config import MUNICIPIOS


def resolver(par: dict, dados: dict, orc_paa: float, msg: bool = False,
             ocupacao_minima: float = 0.0, restringir_paa: bool = True,
             restringir_armazenagem: bool = True) -> dict:
    """Monta e resolve o modelo de programação inteira descrito no README.

    par: saída de montar_parametros(dados)
    dados: saída de limpar_dados()
    orc_paa: OrçPAA (R$)
    ocupacao_minima: fração mínima (0 a 1) dos módulos de cada município que deve ser
        plantada. 0 = não força nada (padrão); 1 = obriga a usar toda a área.
    restringir_paa: False desliga a restrição 4 (orçamento do PAA)
    restringir_armazenagem: False desliga a restrição 2 (armazenagem)
    """
    # ---- CONJUNTOS (índices) -------------------------------------------------
    # k = uma combinação de município e cultura (uma linha da tabela de custos)
    # m = um município; c = uma cultura
    K = par["K"]            # K: as 18 combinações (índices k)
    K_m = par["K_m"]        # K(m): combinações de cada município m {cod_ibge: [k, ...]}
    K_area = par["K_area"]  # K(c) para c em Ce: combinações de cada cultura com limite
                            #   de área estadual {(cultura, safra): [k, ...]}
    K_teto = par["K_teto"]  # K(c) para c em Cn: combinações de cada cultura com teto
                            #   nacional {cultura: [k, ...]}
    K_fam = set(par["K_fam"])  # Kfam: combinações da agricultura familiar
    K_arm = set(par["K_arm"])  # Karm: combinações armazenáveis (grãos e café)

    # ---- PARÂMETROS POR COMBINAÇÃO k ------------------------------------------
    Tam = par["Tam"]      # Tam: tamanho de um módulo (ha)
    Lucro = par["Lucro"]  # Lucro(k): lucro por hectare = receita - custo total (R$/ha)
    Prod = par["Prod"]    # Prod(k): produtividade (kg/ha)
    Preco = par["Preco"]  # Preço(k): valor recebido pelo produtor (R$/kg)

    # ---- PARÂMETROS DE LIMITE -------------------------------------------------
    Area = dados["area_municipio"]    # Área(m): área de lavoura do município m (ha)
    ArmE = dados["armazenagem"]       # ArmE(m): capacidade estática de armazenagem de m (t)
    AreaEst = dados["area_estadual"]  # ÁreaEst(c): limite de área plantada no PR da
                                      #   cultura c, chave (cultura, safra) (ha)
    TetoNac = dados["teto_nacional"]  # TetoNac(c): teto de mercado nacional da cultura c (kg)
    # orc_paa = OrçPAA: orçamento do PAA no Paraná (R$)

    prob = pulp.LpProblem("Safra_Parana", pulp.LpMaximize)

    # variável de decisão: Mód(k) = nº de módulos destinados à combinação k
    # (inteiro >= 0, restrição 6)
    Mod = {k: pulp.LpVariable(f"Mod_{k}", lowBound=0, cat="Integer") for k in K}

    # função objetivo: max Σ Lucro(k) · Tam · Mód(k)
    prob += pulp.lpSum(Lucro[k] * Tam * Mod[k] for k in K)

    restricoes = []  # (descrição, expressão, limite): só para o relatório de uso

    def add(nome, expr, limite, descricao):
        # registra a restrição "expr <= limite" no modelo e no relatório
        prob.addConstraint(expr <= limite, nome)
        restricoes.append((descricao, expr, limite))

    # 1. área de lavoura por município
    for m, ks in K_m.items():
        if ks:
            add(f"Area_{m}", pulp.lpSum(Tam * Mod[k] for k in ks), Area[m],
                f"1. Área - {MUNICIPIOS[m]} (ha)")

    # 2. armazenagem por município (kg -> t)
    if restringir_armazenagem:
        for m, ks in K_m.items():
            ks_arm = [k for k in ks if k in K_arm]
            if ks_arm:
                add(f"Arm_{m}", pulp.lpSum(Prod[k] * Tam * Mod[k] / 1000 for k in ks_arm), ArmE[m],
                    f"2. Armazenagem - {MUNICIPIOS[m]} (t)")

    # 3. área plantada estadual por cultura (e safra, no caso do milho)
    for i, ((cultura, safra), ks) in enumerate(K_area.items()):
        if ks:
            add(f"AreaEst_{i}", pulp.lpSum(Tam * Mod[k] for k in ks), AreaEst[(cultura, safra)],
                f"3. Área estadual - {cultura} {safra} (ha)")

    # 4. orçamento do PAA (agricultura familiar)
    if restringir_paa and K_fam:
        add("PAA", pulp.lpSum(Preco[k] * Prod[k] * Tam * Mod[k] for k in K_fam), orc_paa,
            "4. Orçamento PAA (R$)")

    # 5. teto de mercado nacional por cultura
    for i, (cultura, ks) in enumerate(K_teto.items()):
        if ks:
            add(f"Teto_{i}", pulp.lpSum(Prod[k] * Tam * Mod[k] for k in ks), TetoNac[cultura],
                f"5. Teto nacional - {cultura} (kg)")

    # 7. (opcional) ocupação mínima: força cada município a plantar pelo menos uma
    # fração dos seus módulos, mesmo onde o lucro é negativo
    if ocupacao_minima > 0:
        for m, ks in K_m.items():
            if ks:
                minimo = math.ceil(ocupacao_minima * par["modulos_max"][m])
                prob.addConstraint(pulp.lpSum(Mod[k] for k in ks) >= minimo, f"OcupMin_{m}")

    # resolve com o CBC que já vem com o PuLP
    prob.solve(pulp.PULP_CBC_CMD(msg=msg))
    status = pulp.LpStatus[prob.status]
    if status != "Optimal":
        raise RuntimeError(f"O solver não achou solução ótima (status: {status})")

    # resultado por combinação
    tabela = par["tabela"][["cod_ibge", "produto", "safra", "empreendimento",
                            "prod_kg_ha", "preco_kg", "lucro_ha"]].copy()
    tabela.insert(0, "municipio", tabela["cod_ibge"].map(MUNICIPIOS))
    tabela["modulos"] = [int(round(Mod[k].value())) for k in tabela.index]
    tabela["area_ha"] = tabela["modulos"] * Tam
    tabela["producao_kg"] = tabela["area_ha"] * tabela["prod_kg_ha"]
    tabela["lucro_total"] = tabela["area_ha"] * tabela["lucro_ha"]

    # uso de cada restrição (as que batem no limite são as que seguram o ótimo)
    uso = pd.DataFrame(
        [(d, pulp.value(e), lim) for d, e, lim in restricoes],
        columns=["restricao", "uso", "limite"],
    )
    uso["uso_pct"] = 100 * uso["uso"] / uso["limite"]

    return {
        "status": status,
        "Z": pulp.value(prob.objective),
        "tabela": tabela,
        "restricoes": uso,
        "problema": prob,
    }