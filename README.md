# Safra Paraná

O trabalho descreve a modelagem de dados da agricultura do Paraná, verificando a melhor combinação de culturas agrícolas em seus municípios com o objetivo de maximizar a rentabilidade agrícola total do estado.

## Por quê?

O tema foi escolhido pois a agricultura é uma das bases da economia paranaense. Somente na safra 2025/26, a CONAB estima mais de 5,4 milhões de hectares de soja no estado. Ainda assim, a escolha do que plantar e onde segue o costume ou o preço do momento, sem considerar custos, produtividade e limites de armazenagem simultaneamente. O tema permite aplicar Pesquisa Operacional a um problema real e evidencia conflitos, como o do trigo, que tem margem negativa no estado enquanto o Brasil importa milhões de toneladas anualmente.

## Descrição do problema

O modelo decide quantos módulos de área, de tamanho fixo, cada combinação de município e cultura deve receber para maximizar a margem total do Paraná. A base de custos da CONAB cobre dez municípios paranaenses, que somam 18 combinações de município e cultura divididas em três categorias de produtor: agricultura empresarial, agricultura familiar e sociobiodiversidade. Todas as combinações entram num modelo único, em que cada uma carrega a marcação da sua categoria, e os resultados são analisados separadamente por categoria.

A margem de cada combinação é a receita por hectare (produtividade × preço ao produtor) menos os custos variável e fixo por hectare. A produtividade não vem pronta na base: ela é derivada dividindo o custo por hectare pelo custo por unidade comercializada. Como as unidades originais variam (sacas de 60 kg, sacas de 25 kg, quilos e toneladas), todos os valores são normalizados para kg/ha, R$/kg e R$/ha.

Como a variável de decisão é inteira, o problema é de Programação Inteira, resolvido por Branch & Bound. A relaxação linear resultaria em quantidades fracionárias de módulos.

O modelo respeita os seguintes limites:

- **Área de lavoura por município:** a soma das áreas de todas as culturas e safras não pode passar da área plantada total da PAM/IBGE. A PAM conta a dupla safra duas vezes, e o modelo adota a mesma regra de contagem.
- **Armazenagem por município:** a capacidade estática dos armazéns limita a produção das culturas armazenáveis (grãos, feijão e café). Toda a capacidade é considerada disponível para a produção resultante da otimização.
- **Área plantada estadual por cultura:** vale para soja, milho, feijão, triticale e café, que são as culturas com dado disponível.
- **Orçamento do PAA:** limita o valor total da produção familiar que o estado consegue comprar.
- **Mercado nacional:** teto para soja, milho, trigo e feijão, baseado no balanço de oferta e demanda.

## Dados

### Fontes

- **CONAB: Agricultura e Segurança Alimentar** (Kaggle): https://www.kaggle.com/datasets/brenocodes/conab-agricultura-securanca-alimentar
- **IBGE: Produção Agrícola Municipal (PAM)**, SIDRA, Tabela 5457: https://sidra.ibge.gov.br/tabela/5457

### Dados selecionados

| Arquivo | Uso no modelo | Colunas utilizadas |
|---|---|---|
| `custo_producao.csv` | Custos e produtividade de cada combinação | `municipio`, `cod_ibge`, `uf`, `produto`, `empreendimento`, `safra`, `ano_mes`, `unidade_comercializacao`, `vlr_custo_variavel_ha`, `vlr_custo_variavel_unidade`, `vlr_custo_fixo_ha` |
| `preco_mensal_uf.csv` | Preço recebido pelo produtor no PR | `produto`, `classificao_produto`, `uf`, `ano`, `mes`, `dsc_nivel_comercializacao`, `valor_produto_kg` |
| `armazens_cadastrados.csv` | Capacidade de armazenagem por município | `cod_ibge`, `nom_municipio`, `uf`, `qtd_capacidade_estatica(t)` |
| `levantamento_graos.csv` | Área plantada estadual (grãos) | `ano_agricola`, `uf`, `produto`, `safra`, `area_plantada_mil_ha` |
| `levantamento_cafe.csv` | Área plantada estadual (café) | `ano_agricola`, `uf`, `produto`, `area_plantada_mil_ha` |
| `ppa_propostas_formalizadas_executadas.csv` | Orçamento do PAA no PR | `ano`, `uf`, `cod_ibge`, `valor_formalizado`, `valor_executado` |
| `oferta_demanda.csv` | Teto de mercado nacional | `produto`, `dsc_safra`, `producao_1000t`, `importacao_1000t`, `consumo_1000t`, `exportacao_1000t` |
| PAM/IBGE, Tabela 5457 | Área de lavoura por município (2025, preliminar) | `Cód.`, `Município`, área plantada ou destinada à colheita (Total, ha) |

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

#### Limites por município

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

### Observações sobre os dados

- Na base de café, a coluna `area_plantada_mil_ha` vem em hectares, apesar do nome.
- O trigo do PR não aparece no `levantamento_graos.csv`, então não há limite de área estadual para ele.
- O pinhão e o feijão preto têm um único registro de custo cada, e o último custo do triticale é de 2023.
- Os dados da PAM 2025 são resultados preliminares do IBGE.