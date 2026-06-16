"""
Gera os 3 graficos principais do projeto com dados de 10 anos.
Le do PostgreSQL e salva PNGs em alta resolucao na pasta slides/.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os

DB_CONFIG = {
    "dbname":   "parto_poa",
    "user":     "postgres",
    "password": "1103",
    "host":     "localhost",
    "port":     "5432",
}

PASTA_SLIDES = "slides"
os.makedirs(PASTA_SLIDES, exist_ok=True)

# Paleta consistente com presentacao
CORES_RACA = {
    "Branca": "#E8A87C",
    "Preta": "#85586F",
    "Parda": "#AC7B7B",
    "Amarela": "#F4D03F",
    "Indigena": "#7D5BA6",
}

print("Conectando ao PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
conn.set_client_encoding("UTF8")
print("OK.\n")

# ============================================================
# GRAFICO 1 - Taxa de cesarea por raca (10 anos)
# ============================================================
print("[1/3] Gerando grafico 1: Cesarea por raca (2014-2023)...")
df1 = pd.read_sql("""
    SELECT
        CASE g.raca_cor
            WHEN 1 THEN 'Branca' WHEN 2 THEN 'Preta'
            WHEN 3 THEN 'Amarela' WHEN 4 THEN 'Parda'
            WHEN 5 THEN 'Indigena' END AS raca,
        ROUND(100.0 * SUM(CASE WHEN np.tipo_parto=2 THEN 1 ELSE 0 END)
              / COUNT(*), 2)::float AS taxa_cesarea,
        COUNT(*) AS total
    FROM gestante g
    JOIN nascimento_parto np ON g.id_gestante = np.id_gestante
    WHERE np.tipo_parto IN (1, 2) AND g.raca_cor BETWEEN 1 AND 5
    GROUP BY g.raca_cor
    ORDER BY taxa_cesarea DESC;
""", conn)

fig, ax = plt.subplots(figsize=(10, 6))
cores = [CORES_RACA[r] for r in df1["raca"]]
bars = ax.bar(df1["raca"], df1["taxa_cesarea"], color=cores, edgecolor="white", linewidth=2)
ax.axhline(y=15, color="red", linestyle="--", linewidth=1.5, label="OMS (15%)")
ax.set_ylabel("Taxa de Cesárea (%)", fontsize=12)
ax.set_title("Taxa de Cesárea por Raça/Cor — POA, 2014-2023\nn = 167.319 nascimentos", fontsize=14, pad=15)
ax.set_ylim(0, 70)
ax.legend(loc="upper right")

for bar, val, n in zip(bars, df1["taxa_cesarea"], df1["total"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
            f"{val}%\n(n={n:,})", ha="center", fontsize=10, fontweight="bold")

plt.figtext(0.99, 0.01, "Fonte: SINASC/DATASUS 2014-2023. Elaboração própria.",
            ha="right", fontsize=8, style="italic", color="gray")
plt.tight_layout()
plt.savefig(os.path.join(PASTA_SLIDES, "grafico_1_cesarea_por_raca.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("      Salvo.")

# ============================================================
# GRAFICO 2 - PARADOJA DE SIMPSON (Raca x Escolaridade, 10 anos)
# ============================================================
print("[2/3] Gerando grafico 2: Paradoja de Simpson (2014-2023)...")
df2 = pd.read_sql("""
    SELECT
        CASE g.raca_cor
            WHEN 1 THEN 'Branca' WHEN 2 THEN 'Preta' WHEN 4 THEN 'Parda' END AS raca,
        CASE g.escolaridade
            WHEN 3 THEN '4-7 anos' WHEN 4 THEN '8-11 anos' WHEN 5 THEN '12+ anos' END AS escolaridade,
        ROUND(100.0 * SUM(CASE WHEN np.tipo_parto=2 THEN 1 ELSE 0 END)
              / COUNT(*), 2)::float AS taxa,
        COUNT(*) AS total
    FROM gestante g
    JOIN nascimento_parto np ON g.id_gestante = np.id_gestante
    WHERE np.tipo_parto IN (1, 2)
      AND g.raca_cor IN (1, 2, 4)
      AND g.escolaridade IN (3, 4, 5)
    GROUP BY g.raca_cor, g.escolaridade
    HAVING COUNT(*) >= 100
    ORDER BY g.escolaridade, g.raca_cor;
""", conn)

# Pivot
df2_piv = df2.pivot(index="escolaridade", columns="raca", values="taxa")
df2_piv = df2_piv.reindex(["4-7 anos", "8-11 anos", "12+ anos"])
df2_piv = df2_piv[["Branca", "Preta", "Parda"]]

fig, ax = plt.subplots(figsize=(12, 6.5))
df2_piv.plot(kind="bar", ax=ax, color=[CORES_RACA["Branca"], CORES_RACA["Preta"], CORES_RACA["Parda"]],
             edgecolor="white", linewidth=2, width=0.75)
ax.axhline(y=15, color="red", linestyle="--", linewidth=1.5, label="OMS (15%)")
ax.set_ylabel("Taxa de Cesárea (%)", fontsize=12)
ax.set_xlabel("Escolaridade da Gestante", fontsize=12)
ax.set_title("Taxa de Cesárea por Raça/Cor × Escolaridade — POA, 2014-2023\nA diferença racial desaparece ao controlar por escolaridade",
             fontsize=14, pad=15)
ax.set_ylim(0, 80)
ax.legend(title="Raça/Cor", loc="upper left")
plt.xticks(rotation=0)

for container in ax.containers:
    ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=9, fontweight="bold")

plt.figtext(0.99, 0.01, "Fonte: SINASC/DATASUS 2014-2023. Elaboração própria.",
            ha="right", fontsize=8, style="italic", color="gray")
plt.tight_layout()
plt.savefig(os.path.join(PASTA_SLIDES, "grafico_2_cesarea_raca_escolaridade.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("      Salvo.")

# ============================================================
# GRAFICO 3 NOVO - EVOLUCAO TEMPORAL (cesarea por ano)
# ============================================================
print("[3/3] Gerando grafico 3 NOVO: Evolucao temporal (2014-2023)...")
df3 = pd.read_sql("""
    SELECT
        np.ano,
        COUNT(*) AS total,
        ROUND(100.0 * SUM(CASE WHEN np.tipo_parto=2 THEN 1 ELSE 0 END)
              / NULLIF(SUM(CASE WHEN np.tipo_parto IN (1,2) THEN 1 ELSE 0 END), 0), 2)::float AS taxa_cesarea
    FROM nascimento_parto np
    WHERE np.tipo_parto IN (1, 2)
    GROUP BY np.ano
    ORDER BY np.ano;
""", conn)

fig, ax1 = plt.subplots(figsize=(12, 6.5))

# Barras de nascimentos
ax1.bar(df3["ano"], df3["total"], color="#6A4C93", alpha=0.6, edgecolor="white", linewidth=2, label="Nascimentos")
ax1.set_xlabel("Ano", fontsize=12)
ax1.set_ylabel("Número de Nascimentos", fontsize=12, color="#6A4C93")
ax1.tick_params(axis="y", labelcolor="#6A4C93")
ax1.set_ylim(0, 22000)

for i, (ano, total) in enumerate(zip(df3["ano"], df3["total"])):
    ax1.text(ano, total + 300, f"{total:,}", ha="center", fontsize=9, fontweight="bold", color="#6A4C93")

# Linha de taxa cesarea (eixo secundario)
ax2 = ax1.twinx()
ax2.plot(df3["ano"], df3["taxa_cesarea"], color="#C44569", marker="o", linewidth=3, markersize=10, label="Taxa Cesárea (%)")
ax2.set_ylabel("Taxa de Cesárea (%)", fontsize=12, color="#C44569")
ax2.tick_params(axis="y", labelcolor="#C44569")
ax2.set_ylim(0, 60)
ax2.axhline(y=15, color="red", linestyle="--", linewidth=1, alpha=0.5)
ax2.text(2014, 17, "OMS (15%)", fontsize=9, color="red", style="italic")

for ano, taxa in zip(df3["ano"], df3["taxa_cesarea"]):
    ax2.text(ano, taxa + 1.5, f"{taxa}%", ha="center", fontsize=9, color="#C44569", fontweight="bold")

plt.title("Evolução Temporal: Nascimentos e Taxa de Cesárea — POA, 2014-2023\nQueda de 28,8% nos nascimentos e cesárea estrutural em ~50%",
          fontsize=13, pad=15)
plt.xticks(df3["ano"], rotation=0)

plt.figtext(0.99, 0.01, "Fonte: SINASC/DATASUS 2014-2023. Elaboração própria.",
            ha="right", fontsize=8, style="italic", color="gray")
plt.tight_layout()
plt.savefig(os.path.join(PASTA_SLIDES, "grafico_3_evolucao_temporal.png"),
            dpi=150, bbox_inches="tight")
plt.close()
print("      Salvo.")

conn.close()

print("\n" + "=" * 65)
print("Todos os graficos atualizados com dados de 10 anos!")
print("=" * 65)
print(f"\nArquivos em {os.path.abspath(PASTA_SLIDES)}:")
for arq in sorted(os.listdir(PASTA_SLIDES)):
    if arq.endswith(".png"):
        caminho = os.path.join(PASTA_SLIDES, arq)
        tam_kb = os.path.getsize(caminho) / 1024
        print(f"   - {arq} ({tam_kb:.1f} KB)")