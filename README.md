# Intervenções Médicas e Desigualdades no Parto — Porto Alegre 2014-2023

Uma arquitetura híbrida em PostgreSQL para integrar microdados do SINASC com relatórios da Secretaria Municipal de Saúde de Porto Alegre.

**Autora**: Marina M. Garramones

**Disciplina**: INF01006 — Projeto de Banco de Dados

**Universidade**: UFRGS — Universidade Federal do Rio Grande do Sul

**Ano**: 2026

## 🚀 Aplicação em Produção

🔗 **[Acesse o dashboard interativo →](https://projeto-bd-parto-poa-byv3ws6jdcjfdebesjnemf.streamlit.app/)**

| Componente | Tecnologia |
|---|---|
| Frontend / Dashboard | Streamlit Community Cloud |
| Backend / Banco de Dados | Supabase (PostgreSQL na nuvem) |
| Código fonte | GitHub |

✨ **Acesso público** — não requer instalação nem credenciais.

## 🎯 Sobre o Projeto

Este projeto integra **167.319 nascimentos** registrados em Porto Alegre entre 2014 e 2023 (microdados do SINASC) com **relatórios institucionais** da Secretaria Municipal de Saúde, criando uma arquitetura híbrida que torna visíveis disparidades sociodemográficas hoje fragmentadas em sistemas distintos.

### Principais Achados

1. **Diferença racial aparente**: A taxa de cesárea varia ~12 pontos entre brancas (53%) e pardas (41%) no agregado dos 10 anos.

2. **Paradoxo de Simpson**: Ao controlar por escolaridade, a diferença racial **desaparece**. Universitárias têm ~65% de cesárea independente da raça. A escolaridade é a variável determinante.

3. **Queda demográfica**: Porto Alegre perdeu **28,8% de seus nascimentos** em 10 anos (de 19.189 em 2014 para 13.663 em 2023). A pandemia acelerou a tendência.

4. **Cesárea estrutural**: A taxa global se manteve em ~50%, três vezes a recomendação OMS. Não é coyuntural, é estrutural.

5. **Desigualdade espacial**: Cruzamento dos microdados com indicadores institucionais por distrito sanitário evidencia padrões geográficos de desigualdade na assistência ao parto.

## 🏗️ Arquitetura

### Modelo Híbrido PostgreSQL

| Componente | Tipo | Conteúdo |
|---|---|---|
| gestante | Relacional | Dados sociodemográficos da mãe |
| nascimento_parto | Relacional | Dados do parto (com coluna ano) |
| relatorios_municipais | NoSQL (JSONB) | Documentos institucionais semiestruturados |

### Pipeline ETL

1. **Extração**: Download dos 10 CSVs anuais do SINASC via OpenDataSUS (8.72 GB)
2. **Filtragem**: Seleção dos registros de POA via código IBGE 431490 (167.319 registros)
3. **Carga relacional**: Inserção em tabelas PostgreSQL com normalização de códigos
4. **Carga NoSQL**: Inserção de 9 documentos JSONB com indicadores institucionais
5. **Visualização**: Dashboard Streamlit com filtros temporais e mapa interativo

## 🛠️ Stack Tecnológico

| Camada | Tecnologia |
|---|---|
| Banco de dados | PostgreSQL 16 (relacional + JSONB) hospedado no Supabase |
| Backend / ETL | Python 3.14 + pandas + psycopg2 |
| Frontend | Streamlit + Plotly + Folium |
| Deploy | Streamlit Community Cloud + GitHub |
| Fontes de dados | SINASC/DATASUS, SMS-POA |

## 📁 Estrutura do Repositório

- `dados/` — CSVs e arquivos JSONB
- `scripts/` — Pipeline ETL em Python
- `sql/` — Esquemas e consultas SQL
- `slides/` — Gráficos PNG
- `dashboard_app.py` — Aplicação Streamlit
- `requirements.txt` — Dependências Python

## 🚀 Como Executar Localmente

1. Clonar o repositório: `git clone https://github.com/marinamoli/projeto-bd-parto-poa.git`
2. Instalar dependências: `pip install -r requirements.txt`
3. Configurar arquivo `.env` com credenciais PostgreSQL
4. Executar dashboard: `python -m streamlit run dashboard_app.py`

## 📊 Funcionalidades do Dashboard

O dashboard interativo oferece 5 abas de análise:

1. **Achados Principais** — Gráfico do paradoxo de Simpson (Raça × Escolaridade × Taxa Cesárea)
2. **Evolução Temporal** — Tendências 2014-2023 (nascimentos e cesárea)
3. **Análise Demográfica** — Distribuição por raça, idade e escolaridade
4. **Distritos Sanitários** — Mapa interativo com os 8 distritos de POA + indicadores extraídos do JSONB
5. **Arquitetura** — Documentação técnica do projeto

**Filtros disponíveis**: período temporal, raça/cor, faixa etária, escolaridade.

## 📚 Trabalhos Relacionados

O projeto se posiciona na intersecção de três eixos:

- **Médico-epidemiológico**: Souza et al. (2021), Racismo Obstétrico (2024)
- **Técnico / Engenharia de Dados**: PCDaS/Fiocruz (Elasticsearch), Pegasus/TCU (PostgreSQL)
- **Geográfico-territorial**: Ribeiro et al. (2023) sobre disparidades em POA

## 📄 Fontes de Dados

- [SINASC — Sistema de Informações sobre Nascidos Vivos (DATASUS)](https://datasus.saude.gov.br/transferencia-de-arquivos/)
- [Boletim do Comitê de Prevenção do Óbito Infantil — SMS-POA](https://prefeitura.poa.br/sms)

## 📜 Licença

Projeto acadêmico — INF01006 UFRGS, 2026.
