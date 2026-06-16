"""
Dashboard interativo do projeto de Banco de Dados.
Versao 10 anos: 167.319 nascimentos POA 2014-2023.
Inclui filtro temporal e analise de tendencia.

Executar: python -m streamlit run dashboard_app.py

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURACAO DA PAGINA
# ============================================================
st.set_page_config(
    page_title="Desigualdades no Parto - POA 2014-2023",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main { padding-top: 1rem; }
    [data-testid="stMetricValue"] { font-size: 2.2rem; }
    [data-testid="stMetricLabel"] { font-size: 0.9rem; }
    h1 { color: #6a4c93; }
    h2 { color: #c44569; border-bottom: 2px solid #f0f0f0; padding-bottom: 0.3rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #f8f9fa; border-radius: 8px 8px 0 0; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background: #6a4c93 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONEXAO POSTGRESQL (lee credenciales del .env o Streamlit secrets)
# ============================================================
try:
    DB_CONFIG = {
        "dbname":   st.secrets["DB_NAME"],
        "user":     st.secrets["DB_USER"],
        "password": st.secrets["DB_PASSWORD"],
        "host":     st.secrets["DB_HOST"],
        "port":     st.secrets["DB_PORT"],
    }
except (KeyError, FileNotFoundError, AttributeError):
    DB_CONFIG = {
        "dbname":   os.getenv("DB_NAME", "parto_poa"),
        "user":     os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "host":     os.getenv("DB_HOST", "localhost"),
        "port":     os.getenv("DB_PORT", "5432"),
    }

@st.cache_data(ttl=600)
def carregar_dados():
    """Carrega dados via psycopg2 com encoding UTF8 forcado."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_client_encoding("UTF8")

    df_partos = pd.read_sql("""
        SELECT
            np.id_parto,
            np.ano,
            g.idade_mae,
            CASE g.raca_cor
                WHEN 1 THEN 'Branca' WHEN 2 THEN 'Preta'
                WHEN 3 THEN 'Amarela' WHEN 4 THEN 'Parda'
                WHEN 5 THEN 'Indigena'
                ELSE 'Ignorado' END AS raca_cor,
            g.escolaridade AS escolaridade_num,
            CASE g.escolaridade
                WHEN 1 THEN 'Nenhuma' WHEN 2 THEN '1-3 anos'
                WHEN 3 THEN '4-7 anos' WHEN 4 THEN '8-11 anos'
                WHEN 5 THEN '12+ anos'
                ELSE 'Ignorado' END AS escolaridade,
            CASE
                WHEN g.idade_mae < 20 THEN '< 20'
                WHEN g.idade_mae BETWEEN 20 AND 29 THEN '20-29'
                WHEN g.idade_mae BETWEEN 30 AND 39 THEN '30-39'
                WHEN g.idade_mae >= 40 THEN '40+'
                ELSE 'Ignorado' END AS faixa_etaria,
            CASE np.tipo_parto
                WHEN 1 THEN 'Vaginal'
                WHEN 2 THEN 'Cesareo'
                ELSE 'Ignorado' END AS tipo_parto,
            np.classificacao_robson
        FROM nascimento_parto np
        JOIN gestante g ON np.id_gestante = g.id_gestante;
    """, conn)

    df_distritos = pd.read_sql("""
        SELECT
            conteudo_jsonb->>'distrito_sanitario' AS distrito,
            conteudo_jsonb->>'perfil_socioeconomico' AS perfil,
            (conteudo_jsonb->'indicadores'->>'taxa_cesarea_distrito')::numeric AS taxa_cesarea,
            (conteudo_jsonb->'indicadores'->>'cobertura_prenatal_7_consultas')::numeric AS cobertura_prenatal,
            (conteudo_jsonb->'indicadores'->>'mortalidade_infantil_por_mil')::numeric AS mortalidade_infantil,
            (conteudo_jsonb->'indicadores'->>'proporcao_maes_negras_pct')::numeric AS pct_maes_negras,
            conteudo_jsonb->'infraestrutura'->>'avaliacao_geral' AS infraestrutura,
            (conteudo_jsonb->'infraestrutura'->>'leitos_obstetricos')::integer AS leitos
        FROM relatorios_municipais
        WHERE conteudo_jsonb->>'tipo_documento' = 'relatorio_indicadores_distrito'
        ORDER BY mortalidade_infantil DESC;
    """, conn)

    conn.close()
    return df_partos, df_distritos

df_partos, df_distritos = carregar_dados()

# ============================================================
# SIDEBAR COM FILTROS
# ============================================================
st.sidebar.title("Filtros")
st.sidebar.markdown("---")

# Filtro temporal (slider)
ano_min, ano_max = int(df_partos["ano"].min()), int(df_partos["ano"].max())
anos_selecionados = st.sidebar.slider(
    "Periodo (anos)",
    min_value=ano_min,
    max_value=ano_max,
    value=(ano_min, ano_max),
    step=1
)

# Filtros sociodemograficos (con proteccion contra NaN)
def opciones_seguras(serie):
    """Retorna valores unicos como strings, filtrando NaN."""
    return sorted([x for x in serie.dropna().unique() if isinstance(x, str)])

racas_disponiveis = opciones_seguras(df_partos["raca_cor"])
racas_selecionadas = st.sidebar.multiselect(
    "Raca/Cor",
    options=racas_disponiveis,
    default=racas_disponiveis
)

faixas_disponiveis = ["< 20", "20-29", "30-39", "40+"]
faixas_selecionadas = st.sidebar.multiselect(
    "Faixa Etaria",
    options=faixas_disponiveis,
    default=faixas_disponiveis
)

escolaridades_disponiveis = ["Nenhuma", "1-3 anos", "4-7 anos", "8-11 anos", "12+ anos"]
escolaridades_selecionadas = st.sidebar.multiselect(
    "Escolaridade",
    options=escolaridades_disponiveis,
    default=escolaridades_disponiveis
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Sobre o projeto**")
st.sidebar.info(
    "Marina M. Garramones\n\n"
    "INF01006 - Projeto de BD\n\n"
    "UFRGS\n\n"
    "**SINASC 2014-2023** (10 anos)"
)

# Aplicar filtros
df_filtrado = df_partos[
    (df_partos["ano"] >= anos_selecionados[0]) &
    (df_partos["ano"] <= anos_selecionados[1]) &
    (df_partos["raca_cor"].isin(racas_selecionadas)) &
    (df_partos["faixa_etaria"].isin(faixas_selecionadas)) &
    (df_partos["escolaridade"].isin(escolaridades_selecionadas))
]

# ============================================================
# HEADER
# ============================================================
st.title("Intervencoes Medicas e Desigualdades no Parto")
st.markdown(f"**Porto Alegre, {anos_selecionados[0]}-{anos_selecionados[1]}** - Arquitetura hibrida PostgreSQL (Relacional + NoSQL/JSONB)")
st.markdown("---")

# ============================================================
# KPIS
# ============================================================
col1, col2, col3, col4 = st.columns(4)

total = len(df_filtrado)
df_partos_validos = df_filtrado[df_filtrado["tipo_parto"].isin(["Vaginal", "Cesareo"])]
total_cesarea = (df_partos_validos["tipo_parto"] == "Cesareo").sum()
taxa_cesarea = round(100 * total_cesarea / len(df_partos_validos), 2) if len(df_partos_validos) > 0 else 0
pct_negras = round(100 * df_filtrado["raca_cor"].isin(["Preta", "Parda"]).sum() / total, 2) if total > 0 else 0
idade_media = round(df_filtrado["idade_mae"].mean(), 1) if total > 0 else 0

with col1:
    st.metric(
        "Total de Nascimentos",
        f"{total:,}".replace(",", "."),
        delta=f"de {len(df_partos):,}".replace(",", ".") + " total",
        delta_color="off"
    )
with col2:
    st.metric(
        "Taxa de Cesarea",
        f"{taxa_cesarea}%",
        delta=f"{round(taxa_cesarea - 15, 1)}pp vs OMS",
        delta_color="inverse"
    )
with col3:
    st.metric("Maes Negras (Preta+Parda)", f"{pct_negras}%")
with col4:
    st.metric("Idade Media da Mae", f"{idade_media} anos")

st.markdown("---")

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Achados Principais",
    "Evolucao Temporal",
    "Analise Demografica",
    "Distritos Sanitarios",
    "Arquitetura"
])

# ============================================================
# TAB 1 - ACHADOS
# ============================================================
with tab1:
    st.subheader("Os 3 Achados Encadeados")
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.info("**1. Diferenca racial aparente**\n\nA taxa de cesarea varia significativamente entre racas no agregado dos 10 anos.")
    with col_b:
        st.warning("**2. Paradoxo de Simpson**\n\nAo controlar por escolaridade, a diferenca racial **desaparece**. A escolaridade e determinante.")
    with col_c:
        st.success("**3. Tendencia historica**\n\nQueda demografica de 28.8% em 10 anos: de 19.189 (2014) a 13.663 (2023).")

    st.markdown("### Grafico Principal - Taxa de Cesarea por Raca x Escolaridade")
    st.caption(f"Periodo: {anos_selecionados[0]}-{anos_selecionados[1]} | n = {len(df_partos_validos):,}")

    df_cruzado = df_partos_validos.groupby(["raca_cor", "escolaridade"]).agg(
        total=("tipo_parto", "count"),
        cesareas=("tipo_parto", lambda x: (x == "Cesareo").sum())
    ).reset_index()
    df_cruzado["taxa"] = round(100 * df_cruzado["cesareas"] / df_cruzado["total"], 2)
    df_cruzado = df_cruzado[df_cruzado["total"] >= 100]
    df_cruzado = df_cruzado[df_cruzado["raca_cor"].isin(["Branca", "Preta", "Parda"])]
    df_cruzado = df_cruzado[df_cruzado["escolaridade"].isin(["4-7 anos", "8-11 anos", "12+ anos"])]

    cores = {"Branca": "#E8A87C", "Preta": "#85586F", "Parda": "#AC7B7B"}

    fig = px.bar(
        df_cruzado,
        x="escolaridade", y="taxa", color="raca_cor",
        barmode="group", text="taxa",
        color_discrete_map=cores,
        category_orders={"escolaridade": ["4-7 anos", "8-11 anos", "12+ anos"]},
        labels={"taxa": "Taxa de Cesarea (%)", "escolaridade": "Escolaridade", "raca_cor": "Raca/Cor"}
    )
    fig.add_hline(y=15, line_dash="dash", line_color="red",
                  annotation_text="OMS (15%)", annotation_position="left")
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(height=500, plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")

# ============================================================
# TAB 2 - EVOLUCAO TEMPORAL (NUEVO)
# ============================================================
with tab2:
    st.subheader("Evolucao Temporal 2014-2023")
    st.caption("Analise da serie historica completa")

    col_t1, col_t2 = st.columns(2)

    # Grafico 1: Nascimentos por ano
    with col_t1:
        df_por_ano = df_filtrado.groupby("ano").size().reset_index(name="total")
        fig_t1 = px.line(
            df_por_ano, x="ano", y="total",
            markers=True,
            labels={"total": "Nascimentos", "ano": "Ano"}
        )
        fig_t1.update_traces(line_color="#6a4c93", line_width=3, marker_size=10)
        fig_t1.update_layout(
            height=400, plot_bgcolor="white",
            title="Numero de Nascimentos por Ano"
        )
        st.plotly_chart(fig_t1, width="stretch")

    # Grafico 2: Taxa de cesarea por ano
    with col_t2:
        df_cesarea_ano = df_partos_validos.groupby("ano").agg(
            total=("tipo_parto", "count"),
            cesareas=("tipo_parto", lambda x: (x == "Cesareo").sum())
        ).reset_index()
        df_cesarea_ano["taxa"] = round(100 * df_cesarea_ano["cesareas"] / df_cesarea_ano["total"], 2)

        fig_t2 = px.line(
            df_cesarea_ano, x="ano", y="taxa",
            markers=True, text="taxa",
            labels={"taxa": "Taxa Cesarea (%)", "ano": "Ano"}
        )
        fig_t2.update_traces(line_color="#c44569", line_width=3, marker_size=10,
                             textposition="top center", texttemplate="%{text}%")
        fig_t2.add_hline(y=15, line_dash="dash", line_color="red",
                         annotation_text="OMS (15%)")
        fig_t2.update_layout(
            height=400, plot_bgcolor="white",
            title="Taxa de Cesarea por Ano",
            yaxis=dict(range=[0, 60])
        )
        st.plotly_chart(fig_t2, width="stretch")

    # Grafico 3: Tendencia por raca
    st.markdown("### Evolucao da Taxa de Cesarea por Raca (2014-2023)")

    df_cesarea_raca_ano = df_partos_validos[
        df_partos_validos["raca_cor"].isin(["Branca", "Preta", "Parda"])
    ].groupby(["ano", "raca_cor"]).agg(
        total=("tipo_parto", "count"),
        cesareas=("tipo_parto", lambda x: (x == "Cesareo").sum())
    ).reset_index()
    df_cesarea_raca_ano["taxa"] = round(100 * df_cesarea_raca_ano["cesareas"] / df_cesarea_raca_ano["total"], 2)

    fig_t3 = px.line(
        df_cesarea_raca_ano,
        x="ano", y="taxa", color="raca_cor",
        markers=True,
        color_discrete_map={"Branca": "#E8A87C", "Preta": "#85586F", "Parda": "#AC7B7B"},
        labels={"taxa": "Taxa Cesarea (%)", "ano": "Ano", "raca_cor": "Raca/Cor"}
    )
    fig_t3.add_hline(y=15, line_dash="dash", line_color="red",
                     annotation_text="OMS (15%)")
    fig_t3.update_traces(line_width=2, marker_size=8)
    fig_t3.update_layout(height=450, plot_bgcolor="white")
    st.plotly_chart(fig_t3, width="stretch")

    # Tabela resumo
    st.markdown("### Tabela Resumo Anual")
    df_resumo_anual = df_partos_validos.groupby("ano").agg(
        total_nascimentos=("tipo_parto", "count"),
        cesareas=("tipo_parto", lambda x: (x == "Cesareo").sum()),
        idade_media=("idade_mae", "mean"),
    ).reset_index()
    df_resumo_anual["taxa_cesarea_pct"] = round(100 * df_resumo_anual["cesareas"] / df_resumo_anual["total_nascimentos"], 2)
    df_resumo_anual["idade_media"] = df_resumo_anual["idade_media"].round(1)
    st.dataframe(df_resumo_anual, width="stretch", hide_index=True)

# ============================================================
# TAB 3 - ANALISE DEMOGRAFICA
# ============================================================
with tab3:
    col_e, col_f = st.columns(2)

    with col_e:
        st.subheader("Taxa de Cesarea por Raca/Cor")
        df_raca = df_partos_validos.groupby("raca_cor").agg(
            total=("tipo_parto", "count"),
            cesareas=("tipo_parto", lambda x: (x == "Cesareo").sum())
        ).reset_index()
        df_raca["taxa"] = round(100 * df_raca["cesareas"] / df_raca["total"], 2)
        df_raca = df_raca[df_raca["total"] >= 100].sort_values("taxa", ascending=False)

        fig2 = px.bar(
            df_raca, x="raca_cor", y="taxa", text="taxa",
            color="raca_cor",
            color_discrete_map={
                "Branca": "#E8A87C", "Preta": "#85586F", "Parda": "#AC7B7B",
                "Amarela": "#F4D03F", "Indigena": "#7D5BA6"
            },
            labels={"taxa": "Taxa de Cesarea (%)", "raca_cor": ""}
        )
        fig2.add_hline(y=15, line_dash="dash", line_color="red", annotation_text="OMS")
        fig2.update_traces(texttemplate="%{text}%", textposition="outside")
        fig2.update_layout(showlegend=False, height=400, plot_bgcolor="white")
        st.plotly_chart(fig2, width="stretch")

    with col_f:
        st.subheader("Distribuicao por Faixa Etaria")
        df_idade = df_filtrado[df_filtrado["faixa_etaria"] != "Ignorado"].groupby("faixa_etaria").size().reset_index(name="total")
        df_idade = df_idade.sort_values("faixa_etaria")

        fig3 = px.pie(
            df_idade, names="faixa_etaria", values="total", hole=0.5,
            color_discrete_sequence=px.colors.sequential.Purp_r
        )
        fig3.update_traces(textinfo="percent+label")
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, width="stretch")

    st.subheader("Detalhamento por Raca e Escolaridade")
    df_detalhe = df_partos_validos.groupby(["raca_cor", "escolaridade"]).agg(
        total=("tipo_parto", "count"),
        idade_media=("idade_mae", "mean"),
        taxa_cesarea=("tipo_parto", lambda x: round(100 * (x == "Cesareo").sum() / len(x), 2))
    ).reset_index()
    df_detalhe["idade_media"] = df_detalhe["idade_media"].round(1)
    st.dataframe(df_detalhe, width="stretch", hide_index=True)

# ============================================================
# TAB 4 - DISTRITOS
# ============================================================
with tab4:
    st.subheader("Dados extraidos do modelo NoSQL/JSONB")
    st.caption("Os 8 distritos sanitarios simulados + 1 documento real do Boletim oficial SMS-POA")

    col_g, col_h = st.columns(2)

    with col_g:
        fig4 = px.bar(
            df_distritos.sort_values("mortalidade_infantil"),
            x="mortalidade_infantil", y="distrito", orientation="h",
            color="perfil", text="mortalidade_infantil",
            color_discrete_map={
                "alto": "#27ae60", "medio": "#3498db",
                "medio_baixo": "#e67e22", "baixo": "#c0392b"
            },
            labels={"mortalidade_infantil": "Mortalidade Infantil (por mil)", "distrito": ""}
        )
        fig4.update_traces(textposition="outside")
        fig4.update_layout(height=400, plot_bgcolor="white", title="Mortalidade Infantil por Distrito")
        st.plotly_chart(fig4, width="stretch")

    with col_h:
        fig5 = px.scatter(
            df_distritos,
            x="pct_maes_negras", y="taxa_cesarea",
            size="leitos", color="perfil",
            hover_name="distrito",
            color_discrete_map={
                "alto": "#27ae60", "medio": "#3498db",
                "medio_baixo": "#e67e22", "baixo": "#c0392b"
            },
            labels={
                "pct_maes_negras": "% Maes Negras",
                "taxa_cesarea": "Taxa de Cesarea (%)",
                "leitos": "Leitos"
            }
        )
        fig5.update_layout(height=400, plot_bgcolor="white",
                          title="Correlacao: % Maes Negras vs Cesarea")
        st.plotly_chart(fig5, width="stretch")

    st.subheader("Tabela Completa dos Distritos")
    st.dataframe(df_distritos, width="stretch", hide_index=True)

# ============================================================
# TAB 5 - ARQUITETURA
# ============================================================
with tab5:
    st.subheader("Arquitetura Hibrida do Projeto")

    col_i, col_j, col_k = st.columns(3)

    with col_i:
        st.markdown("### Modelo Relacional")
        st.markdown(
            "**Tabelas:**\n"
            "- gestante\n"
            "- nascimento_parto (com coluna ano)\n\n"
            "**Dados:**\n"
            "- 167.319 nascimentos\n"
            "- Fonte: SINASC 2014-2023\n\n"
            "**Operadores SQL:**\n"
            "- JOIN, GROUP BY\n"
            "- WINDOW FUNCTIONS\n"
            "- Filtros temporais"
        )

    with col_j:
        st.markdown("### Modelo NoSQL (JSONB)")
        st.markdown(
            "**Tabela:**\n"
            "- relatorios_municipais\n\n"
            "**Dados:**\n"
            "- 8 docs simulados\n"
            "- 1 doc REAL (SMS-POA)\n\n"
            "**Operadores JSONB:**\n"
            "- `->` (acesso JSON)\n"
            "- `->>` (acesso como texto)\n"
            "- `@>` (contencao)"
        )

    with col_k:
        st.markdown("### PostgreSQL Hibrido")
        st.markdown(
            "**Vantagens:**\n"
            "- Tudo em 1 SGBD\n"
            "- SQL + JSONB nativos\n"
            "- Indices GIN no JSONB\n"
            "- Indice em ano para filtros\n\n"
            "**Volumes:**\n"
            "- Brasil: 27 milhoes\n"
            "- POA: 167.319"
        )

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "Dashboard gerado em tempo real via PostgreSQL. "
    "Fontes: SINASC/DATASUS 2014-2023 - Boletim SMS-POA Nov/2024. "
    "Marina M. Garramones - UFRGS 2026"
)