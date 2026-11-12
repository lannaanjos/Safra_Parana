# Safra Paraná

O trabalho descreve a modelagem de dados da agricultura do Paraná, verificando a melhor combinação de culturas agrícolas em seus municípios com o objetivo de maximizar a rentabilidade agrícola total do estado.

## Justificativa do tema

A distribuição adequada de culturas agrícolas foi o tema escolhido pois a economia do Paraná se beneficia do agronegócio, que representa cerca de 35% do PIB paranaense. O estado é o 2º maior produtor de grãos do país, destacando-se com o cultivo da soja, milho, trigo e feijão. Segundo o portal [Bem Paraná](https://www.bemparana.com.br/opiniao/parana-recorde-no-agro-traduz-a-forca-da-quarta-maior-economia-do-pais/), somente em 2025, a agricultura estadual rendeu R$ 91,2 bilhões de valor bruto de produção.

Com base nisso, o grupo decidiu analisar a dispersão dos diferentes tipos de culturas pelo Paraná pelos municípios representativos, eleitos pela CONAB, visando avaliar a estrutura atual e propor uma alternativa que maximize a produção e rentabilidade agrícuola estadual.

## Descrição do problema

A área cultivável de cada um dos 10 municípios foi dividida em módulos iguais de *x* hectares. O modelo decidirá quantos módulos de cada município serão destinados a cada cultura possível nele para maximizar a produção e rentabilidade total.

Ao total, com a base de custos da CONAB, temos 18 combinações de município e cultura divididas entre três categorias de produtor: agricultura familiar, sociobiodiversidade e agricultura empresarial. Cada combinação é classificada conforme sua categoria e os resultados seão analisados conforme essa classificação.

Para cada cultura em cada município, calcula-se o lucro por hectare através da receita obtida em um hectare menos o custo variável e o custo fixo desse hectare.

> Lucro por hectare = receita obtida no hectare - custos do hectare

A produtividade é determinada pela quantidade de sacas que um hectar produz. Como a CONAB não informa o quantidade de sacas exatas, utilizamos o seguinte cálculo:

> Produtividade (sacas por hectare) = custo por hectare / custo por saca

Como as unidades variam no dataset original, os valores serão normalizados da seguinte maneira:
- Produtividade: kg/ha (quilograma por hectare).
- Preço do quilo vendido: R$/kg (real por quilograma).
- Valor em dinheiro de um hectare: R$/ha (real por hectare).

### Limites

#### Área cultivável e capacidade de armazenamento por município

| Município | Área de lavoura PAM 2025 (ha) | Capacidade estática (t) |
|---|---|---|
| Cascavel | 249.637 | 1.236.110 |
| Londrina | 139.946 | 378.730 |
| Guarapuava | 136.230 | 1.538.570 |
| Prudentópolis | 92.743 | 83.000 |
| Ponta Grossa | 92.263 | 2.541.830 |
| Dois Vizinhos | 41.713 | 172.820 |
| Francisco Beltrão | 35.697 | 134.030 |
| Capanema | 31.063 | 62.480 |
| Umuarama | 18.732 | 110.290 |
| Contenda | 15.843 | 38.520 |

#### Combinações de município e cultura

| Município | Culturas | Categoria |
|---|---|---|
| Ponta Grossa | soja, milho 1ª safra, feijão cores, trigo, triticale | empresarial |
| Londrina | soja, milho 2ª safra, trigo | empresarial |
| Londrina | café | familiar |
| Cascavel | trigo | empresarial |
| Cascavel | milho 2ª safra | familiar |
| Capanema | trigo | familiar |
| Dois Vizinhos | trigo | familiar |
| Francisco Beltrão | feijão cores | familiar |
| Prudentópolis | feijão preto | familiar |
| Contenda | batata | familiar |
| Umuarama | mandioca | familiar |
| Guarapuava | pinhão | sociobiodiversidade |


## Modelagem formal

### Conjuntos

| Símbolo | Significado |
|---|---|
| M | Municípios do estudo (10) |
| C | Culturas |
| K | Combinações (m, c) de município e cultura disponíveis na base de custos (18) |
| K(m) | Combinações do município m |
| K(c) | Combinações da cultura c |
| F | Combinações da agricultura familiar |
| S | Combinações armazenáveis (grãos, feijão e café) |
| E | Culturas com área plantada estadual disponível (soja, milho, feijão, triticale, café) |
| N | Culturas com teto de mercado nacional (soja, milho, feijão, trigo) |

### Variável de decisão

x_k ∈ ℤ₊: número de módulos de área destinados à combinação k.

### Função objetivo

Maximizar a margem total do estado, em R$:

max Z = Σ_{k ∈ K} m_k · t · x_k (área de cada combinação x lucro por hectare, somada a todas as combinações)

### Restrições

1. **Área de lavoura por município.** A soma das áreas de todas as culturas e safras não pode passar da área da produção agrícola municipal, que usa a mesma regra de contagem da dupla safra:
   Σ_{k ∈ K(m)} t · x_k ≤ A_m, para todo m ∈ M

2. **Armazenagem por município.** A produção das culturas armazenáveis não pode passar da capacidade estática (a divisão por 1.000 converte kg em t):
   Σ_{k ∈ K(m) ∩ S} q_k · t · x_k / 1000 ≤ W_m, para todo m ∈ M

3. **Área plantada estadual por cultura:**
   Σ_{k ∈ K(c)} t · x_k ≤ E_c, para todo c ∈ E

4. **Orçamento do PAA.** O valor da produção familiar comprada pelo estado não pode passar do orçamento:
   Σ_{k ∈ F} p_k · q_k · t · x_k ≤ B

5. **Teto de mercado nacional:**
   Σ_{k ∈ K(c)} q_k · t · x_k ≤ N_c, para todo c ∈ N

6. **Domínio:**
   x_k ∈ ℤ₊, para todo k ∈ K

## Dados

### Fontes

- **CONAB: Agricultura e Segurança Alimentar** (Kaggle): https://www.kaggle.com/datasets/brenocodes/conab-agricultura-securanca-alimentar
- **IBGE: Produção Agrícola Municipal (PAM)**, SIDRA, Tabela 5457: https://sidra.ibge.gov.br/tabela/5457

### Conjunto de informações utilizado

| Arquivo | Uso no modelo | Colunas utilizadas |
|---|---|---|
| `custo_producao.csv` | Custos e produtividade de cada combinação | `municipio`, `uf`, `produto`, `empreendimento`, `safra`, `mes`, `unidade_comercializacao`, `vlr_custo_variavel_ha`, `vlr_custo_variavel_unidade`, `vlr_custo_fixo_ha`, `vlr_renda_fator_h` |
| `preco_mensal_uf.csv` | Preço recebido pelo produtor no PR | `produto`, `classificao_produto`, `uf`, `mes`, `dsc_nivel_comercializacao`, `valor_produto_kg` |
| `armazens_cadastrados.csv` | Capacidade de armazenagem por município | `nom_municipio`, `uf`, `qtd_capacidade_estatica(t)`, `identificacao_armazem` |
| `levantamento_graos.csv` | Área plantada estadual (grãos) | `ano_agricola`, `uf`, `produto`, `safra`, `area_plantada_mil_ha` |
| `levantamento_cafe.csv` | Área plantada estadual (café) | `ano_agricola`, `uf`, `produto`, `area_plantada_mil_ha` |
| `ppa_propostas_formalizadas_executadas.csv` | Orçamento do PAA no PR | `ano`, `uf`, `cod_ibge`, `valor_formalizado`, `valor_executado` |
| `oferta_demanda.csv` | Teto de mercado nacional | `produto`, `dsc_safra`, `producao_1000t`, `importacao_1000t`, `consumo_1000t`, `exportacao_1000t` |
| PAM/IBGE, Tabela 5457 | Área de lavoura por município (2025, preliminar) | `Município`, área plantada ou destinada à colheita (Total, ha) |

### Observações sobre os dados

- Na base de café, a coluna `area_plantada_mil_ha` vem em hectares, apesar do nome.
- O trigo do PR não aparece no `levantamento_graos.csv`, então não há limite de área estadual para ele.
- O pinhão e o feijão preto têm um único registro de custo cada, e o último custo do triticale é de 2023.
- Os dados da PAM 2025 são resultados preliminares do IBGE.

## Por que usar Programação Inteira?

Como a variável de decisão é inteira, o problema é de Programação Inteira porque a decisão de alocação se dá em módulos indivisíveis, no caso, as áreas de plantio. E como, precisamos verificar a "combinação ótima", usa-se Branch & Bound.