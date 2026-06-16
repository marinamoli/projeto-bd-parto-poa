"""
Carga dos dados consolidados 2014-2023 do SINASC POA no PostgreSQL.
Le o CSV unificado e insere ~167.000 registros nas tabelas gestante
e nascimento_parto.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
import time

DB_CONFIG = {
    "dbname":   "parto_poa",
    "user":     "postgres",
    "password": "1103",
    "host":     "localhost",
    "port":     "5432",
}

PASTA_DADOS = "dados"
ARQUIVO_CSV = os.path.join(PASTA_DADOS, "sinasc_poa_2014_2023.csv")

print("=" * 65)
print("Carga dos dados SINASC 2014-2023 - Porto Alegre")
print("=" * 65)

# === ETAPA 1: LER CSV ===
print(f"\n[1/4] Lendo {ARQUIVO_CSV}...")
df = pd.read_csv(ARQUIVO_CSV, sep=";", encoding="utf-8")
print(f"      Registros lidos: {len(df):,}")
print(f"      Colunas: {list(df.columns)}")

df = df.astype(object).where(pd.notnull(df), None)

# === ETAPA 2: CONECTAR ===
print(f"\n[2/4] Conectando ao PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
print("      Conexao OK.")

# === ETAPA 3: LIMPAR ===
print(f"\n[3/4] Limpando dados antigos...")
cur.execute("TRUNCATE TABLE nascimento_parto, gestante RESTART IDENTITY CASCADE;")
conn.commit()
print("      Tabelas limpas.")

# === ETAPA 4: INSERIR ===
print(f"\n[4/4] Inserindo {len(df):,} registros...")
inicio = time.time()

def converter(v):
    if v is None or pd.isna(v):
        return None
    if isinstance(v, float):
        return int(v) if v.is_integer() else v
    return v

dados = []
for _, row in df.iterrows():
    dados.append((
        converter(row.get("IDADEMAE")),
        converter(row.get("RACACOR")),
        converter(row.get("ESCMAE")),
        str(row.get("CODMUNRES")) if row.get("CODMUNRES") is not None else None,
        converter(row.get("PARTO")),
        converter(row.get("TPROBSON")),
        converter(row.get("STTRABPART")),
        converter(row.get("ANO")),
    ))

sql_insercao = """
    WITH nova_gestante AS (
        INSERT INTO gestante (idade_mae, raca_cor, escolaridade, cod_municipio)
        VALUES (%s, %s, %s, %s)
        RETURNING id_gestante
    )
    INSERT INTO nascimento_parto (
        id_gestante, tipo_parto, classificacao_robson, status_trab_parto, ano
    )
    SELECT id_gestante, %s, %s, %s, %s FROM nova_gestante;
"""

execute_batch(cur, sql_insercao, dados, page_size=1000)
conn.commit()

duracao = time.time() - inicio
print(f"      Inseridos em {duracao:.1f} segundos.")

# === VERIFICACAO ===
print("\n" + "=" * 65)
print("VERIFICACAO FINAL")
print("=" * 65)

cur.execute("SELECT COUNT(*) FROM gestante;")
total_g = cur.fetchone()[0]
print(f"\nTotal gestantes:   {total_g:,}")

cur.execute("SELECT COUNT(*) FROM nascimento_parto;")
total_p = cur.fetchone()[0]
print(f"Total nascimentos: {total_p:,}")

cur.execute("""
    SELECT ano, COUNT(*) as total
    FROM nascimento_parto
    GROUP BY ano ORDER BY ano;
""")
print("\nDistribuicao por ano:")
for ano, total in cur.fetchall():
    print(f"   {ano}: {total:,}")

cur.execute("""
    SELECT
        CASE tipo_parto
            WHEN 1 THEN 'Vaginal'
            WHEN 2 THEN 'Cesareo'
            ELSE 'Ignorado' END,
        COUNT(*),
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
    FROM nascimento_parto
    GROUP BY tipo_parto
    ORDER BY tipo_parto;
""")
print("\nDistribuicao por tipo de parto:")
for tipo, total, pct in cur.fetchall():
    print(f"   {tipo:15s}: {total:7,} ({pct}%)")

cur.close()
conn.close()
print("\n" + "=" * 65)
print("Carga 10 anos concluida!")
print("=" * 65)