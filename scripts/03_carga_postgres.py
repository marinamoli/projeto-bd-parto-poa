"""
Script de carga dos dados filtrados do SINASC 2023 (Porto Alegre)
no banco de dados PostgreSQL.

Le o CSV gerado pelo script 02_filtrar_poa.py e insere os registros
nas tabelas relacionais 'gestante' e 'nascimento_parto'.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import os
import time

# === CONFIGURACOES DE CONEXAO ===
# IMPORTANTE: Ajuste a senha para a que voce definiu na instalacao do PostgreSQL
DB_CONFIG = {
    "dbname":   "parto_poa",
    "user":     "postgres",
    "password": "1103",      
    "host":     "localhost",
    "port":     "5432",
}

# === ARQUIVO DE ENTRADA ===
PASTA_DADOS = "dados"
ARQUIVO_CSV = os.path.join(PASTA_DADOS, "sinasc_poa_2023.csv")

print("=" * 65)
print("Carga dos dados do SINASC 2023 - Porto Alegre")
print("Destino: PostgreSQL - banco 'parto_poa'")
print("=" * 65)

# === ETAPA 1: LER O CSV ===
print(f"\n[1/4] Lendo arquivo {ARQUIVO_CSV}...")
df = pd.read_csv(ARQUIVO_CSV, sep=";", encoding="utf-8")
print(f"      Registros lidos: {len(df):,}")
print(f"      Colunas: {list(df.columns)}")

# Substituir NaN por None (para PostgreSQL aceitar como NULL)
df = df.astype(object).where(pd.notnull(df), None)

# === ETAPA 2: CONECTAR AO POSTGRESQL ===
print(f"\n[2/4] Conectando ao PostgreSQL...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("      Conexao estabelecida com sucesso.")
except Exception as e:
    print(f"      ERRO na conexao: {e}")
    print("      Verifique:")
    print("      - PostgreSQL esta rodando?")
    print("      - A senha em DB_CONFIG esta correta?")
    raise SystemExit(1)

# === ETAPA 3: LIMPAR DADOS ANTERIORES (TRUNCATE para reexecucao segura) ===
print(f"\n[3/4] Limpando dados antigos (TRUNCATE)...")
cur.execute("TRUNCATE TABLE nascimento_parto, gestante RESTART IDENTITY CASCADE;")
conn.commit()
print("      Tabelas limpas.")

# === ETAPA 4: INSERIR DADOS ===
print(f"\n[4/4] Inserindo {len(df):,} registros...")
inicio = time.time()

# Convertendo valores para tipos Python nativos (psycopg2 nao gosta de tipos numpy)
def converter(v):
    if v is None:
        return None
    if pd.isna(v):
        return None
    if isinstance(v, float):
        return int(v) if v.is_integer() else v
    return v

dados_para_inserir = []
for _, row in df.iterrows():
    dados_para_inserir.append((
        converter(row.get("IDADEMAE")),
        converter(row.get("RACACOR")),
        converter(row.get("ESCMAE")),
        str(row.get("CODMUNRES")) if row.get("CODMUNRES") is not None else None,
        converter(row.get("PARTO")),
        converter(row.get("TPROBSON")),
        converter(row.get("STTRABPART")),
    ))

# Inserir gestante + nascimento_parto em uma operacao unica usando WITH
sql_insercao = """
    WITH nova_gestante AS (
        INSERT INTO gestante (idade_mae, raca_cor, escolaridade, cod_municipio)
        VALUES (%s, %s, %s, %s)
        RETURNING id_gestante
    )
    INSERT INTO nascimento_parto (
        id_gestante, tipo_parto, classificacao_robson, status_trab_parto
    )
    SELECT id_gestante, %s, %s, %s FROM nova_gestante;
"""

# execute_batch e MUITO mais rapido que iterar fila por fila
execute_batch(cur, sql_insercao, dados_para_inserir, page_size=500)
conn.commit()

duracao = time.time() - inicio
print(f"      Insercao concluida em {duracao:.1f} segundos.")

# === VERIFICACAO ===
print("\n" + "=" * 65)
print("VERIFICACAO FINAL")
print("=" * 65)

cur.execute("SELECT COUNT(*) FROM gestante;")
total_gestantes = cur.fetchone()[0]
print(f"\nTotal de gestantes inseridas:        {total_gestantes:,}")

cur.execute("SELECT COUNT(*) FROM nascimento_parto;")
total_partos = cur.fetchone()[0]
print(f"Total de nascimentos inseridos:      {total_partos:,}")

cur.execute("""
    SELECT
        CASE tipo_parto
            WHEN 1 THEN 'Vaginal'
            WHEN 2 THEN 'Cesareo'
            ELSE 'Desconhecido'
        END AS tipo,
        COUNT(*) AS total,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
    FROM nascimento_parto
    GROUP BY tipo_parto
    ORDER BY tipo_parto;
""")
print("\nDistribuicao por tipo de parto (do banco de dados):")
for tipo, total, pct in cur.fetchall():
    print(f"   {tipo:15s}: {total:6,} ({pct:5.2f}%)")

cur.close()
conn.close()

print("\n" + "=" * 65)
print("Carga concluida com sucesso! Dados prontos para consultas.")
print("=" * 65)