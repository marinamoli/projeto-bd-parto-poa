"""
Script de carga dos documentos JSON na tabela relatorios_municipais
do PostgreSQL (componente NoSQL da arquitetura hibrida).

Carrega tanto os 8 documentos simulados quanto o documento real
extraido do boletim oficial da SMS-POA.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import psycopg2
import json
import os

# === CONFIGURACOES ===
DB_CONFIG = {
    "dbname":   "parto_poa",
    "user":     "postgres",
    "password": "1103",
    "host":     "localhost",
    "port":     "5432",
}

PASTA_JSON = "dados/relatorios_json"

print("=" * 65)
print("Carga dos documentos JSON na tabela relatorios_municipais")
print("Componente NoSQL/JSONB da arquitetura hibrida")
print("=" * 65)

# === ETAPA 1: LISTAR ARQUIVOS JSON ===
print(f"\n[1/4] Listando arquivos em {PASTA_JSON}/")
arquivos = sorted([f for f in os.listdir(PASTA_JSON) if f.endswith(".json")])
print(f"      Encontrados: {len(arquivos)} arquivos")
for arq in arquivos:
    tipo = "[REAL]    " if "REAL" in arq else "[SIMULADO]"
    print(f"      {tipo} {arq}")

# === ETAPA 2: CONECTAR ===
print(f"\n[2/4] Conectando ao PostgreSQL...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("      Conexao estabelecida.")
except Exception as e:
    print(f"      ERRO: {e}")
    raise SystemExit(1)

# === ETAPA 3: LIMPAR DADOS ANTERIORES ===
print(f"\n[3/4] Limpando tabela relatorios_municipais...")
cur.execute("TRUNCATE TABLE relatorios_municipais RESTART IDENTITY;")
conn.commit()
print("      Tabela limpa.")

# === ETAPA 4: INSERIR DOCUMENTOS ===
print(f"\n[4/4] Inserindo documentos JSON...")
inseridos = 0
for arq in arquivos:
    caminho = os.path.join(PASTA_JSON, arq)
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = json.load(f)

    # Extrair data de referencia do JSON
    data_ref = (
        conteudo.get("data_referencia")
        or conteudo.get("data_publicacao")
        or "2023-12-31"
    )

    cur.execute(
        """
        INSERT INTO relatorios_municipais (data_referencia, conteudo_jsonb)
        VALUES (%s, %s::jsonb);
        """,
        (data_ref, json.dumps(conteudo)),
    )
    inseridos += 1

conn.commit()
print(f"      {inseridos} documentos inseridos com sucesso.")

# === VERIFICACAO ===
print("\n" + "=" * 65)
print("VERIFICACAO DA CARGA")
print("=" * 65)

cur.execute("SELECT COUNT(*) FROM relatorios_municipais;")
total = cur.fetchone()[0]
print(f"\nTotal de documentos na tabela: {total}")

# Verificar tipos de documento usando operadores JSONB nativos
cur.execute("""
    SELECT
        conteudo_jsonb->>'tipo_documento' AS tipo,
        COUNT(*) AS quantidade
    FROM relatorios_municipais
    GROUP BY conteudo_jsonb->>'tipo_documento';
""")
print("\nDistribuicao por tipo de documento:")
for tipo, qtd in cur.fetchall():
    print(f"   - {tipo}: {qtd}")

# Verificar documento REAL
cur.execute("""
    SELECT
        conteudo_jsonb->>'fonte' AS fonte,
        conteudo_jsonb->'indicadores_principais'->>'taxa_mortalidade_infantil_por_mil' AS taxa_mort
    FROM relatorios_municipais
    WHERE conteudo_jsonb->>'natureza_dados' LIKE '%REAL%';
""")
print("\nDocumento REAL identificado:")
for fonte, taxa in cur.fetchall():
    print(f"   Fonte: {fonte}")
    print(f"   Taxa de mortalidade infantil 2022: {taxa} por mil nascidos vivos")

cur.close()
conn.close()

print("\n" + "=" * 65)
print("Carga concluida! A arquitetura hibrida esta completa:")
print("  - 13.663 nascimentos no modelo relacional")
print(f"  - {total} documentos no modelo NoSQL (JSONB)")
print("=" * 65)