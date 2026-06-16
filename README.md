\# Intervenções Médicas e Desigualdades no Parto — Porto Alegre 2014-2023



> Uma arquitetura híbrida em PostgreSQL para integrar microdados do SINASC com relatórios da Secretaria Municipal de Saúde de Porto Alegre.



\*\*Autora\*\*: Marina M. Garramones

\*\*Disciplina\*\*: INF01006 — Projeto de Banco de Dados

\*\*Universidade\*\*: UFRGS — Universidade Federal do Rio Grande do Sul

\*\*Ano\*\*: 2026



\## 📊 Dashboard ao Vivo



🔗 \*\*\[Ver dashboard interativo](https://SEU-LINK.streamlit.app)\*\* \_(em breve)\_



\## 🎯 Sobre o Projeto



Este projeto integra \*\*167.319 nascimentos\*\* registrados em Porto Alegre entre 2014 e 2023 (microdados do SINASC) com \*\*relatórios institucionais\*\* da Secretaria Municipal de Saúde, criando uma arquitetura híbrida que torna visíveis disparidades sociodemográficas hoje fragmentadas em sistemas distintos.



\### Principais achados



1\. \*\*Diferença racial aparente\*\*: A taxa de cesárea varia 12 pontos entre brancas (53%) e pardas (41%) no agregado dos 10 anos.



2\. \*\*Paradoxo de Simpson\*\*: Ao controlar por escolaridade, a diferença racial \*\*desaparece\*\*. Universitárias têm \~65% de cesárea independente da raça. A escolaridade é a variável determinante.



3\. \*\*Queda demográfica\*\*: Porto Alegre perdeu \*\*28,8% de seus nascimentos\*\* em 10 anos (de 19.189 em 2014 para 13.663 em 2023). A pandemia acelerou a tendência.



4\. \*\*Cesárea estrutural\*\*: A taxa global se manteve em \~50%, três vezes a recomendação OMS. Não é coyuntural, é estrutural.



\## 🏗️ Arquitetura



\### Modelo Híbrido PostgreSQL



| Componente | Tipo | Conteúdo |

|---|---|---|

| `gestante` | Relacional | Dados sociodemográficos da mãe |

| `nascimento\_parto` | Relacional | Dados do parto (com coluna `ano`) |

| `relatorios\_municipais` | NoSQL (JSONB) | Documentos institucionais semiestruturados |



\### Pipeline ETL

