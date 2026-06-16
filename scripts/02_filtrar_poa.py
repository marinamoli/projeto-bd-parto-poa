"""
Script de exploracao e filtragem dos microdados do SINASC 2023.
Filtra apenas Porto Alegre (codigo IBGE 431490) e seleciona as
colunas relevantes para o projeto.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import pandas as pd
import os

# Configuracoes
PASTA_DADOS = "dados"
ARQUIVO_ORIGEM = os.path.join(PASTA_DADOS, "SINASC_2023.csv")
ARQUIVO_DESTINO = os.path.join(PASTA_DADOS, "sinasc_poa_2023.csv")
COD_MUNICIPIO_POA = "431490"  # Codigo IBGE de Porto Alegre

# Colunas do projeto conforme anteprojeto (Tabela 1 - Dicionario de Dados)
COLUNAS_PROJETO = [
    "NUMERODN",      # Numero da Declaracao de Nascido Vivo
    "IDADEMAE",      # Idade da mae
    "RACACOR",       # Raca/cor da mae
    "ESCMAE",        # Escolaridade da mae
    "CODMUNRES",     # Codigo IBGE do municipio de residencia
    "PARTO",         # Tipo de parto (1=Vaginal, 2=Cesareo)
    "TPROBSON",      # Classificacao de Robson
    "STTRABPART",    # Status do trabalho de parto
]

print("=" * 65)
print("Exploracao e Filtragem do SINASC 2023")
print("Filtro: Porto Alegre (codigo IBGE 431490)")
print("=" * 65)

# Etapa 1: Leitura do cabecalho para descobrir quais colunas existem
print(f"\n[1/4] Lendo cabecalho de: {ARQUIVO_ORIGEM}")

df_header = pd.read_csv(ARQUIVO_ORIGEM, sep=";", nrows=0, encoding="latin-1")
colunas_disponiveis = list(df_header.columns)

print(f"      Total de colunas no arquivo: {len(colunas_disponiveis)}")

colunas_existentes = [c for c in COLUNAS_PROJETO if c in colunas_disponiveis]
colunas_faltantes = [c for c in COLUNAS_PROJETO if c not in colunas_disponiveis]

print(f"      Colunas do projeto encontradas: {len(colunas_existentes)}/8")
if colunas_faltantes:
    print(f"      Colunas faltantes: {colunas_faltantes}")

# Etapa 2: Leitura completa apenas das colunas relevantes
print(f"\n[2/4] Carregando apenas as colunas relevantes...")
print("      (pode levar 1-2 minutos pelo tamanho do arquivo)")

colunas_carregar = list(set(colunas_existentes + ["CODMUNRES"]))

df = pd.read_csv(
    ARQUIVO_ORIGEM,
    sep=";",
    encoding="latin-1",
    usecols=colunas_carregar,
    dtype={"CODMUNRES": str, "NUMERODN": str},
    low_memory=False,
)

print(f"      Registros lidos (Brasil inteiro): {len(df):,}")

# Etapa 3: Filtro por Porto Alegre
print(f"\n[3/4] Filtrando registros de Porto Alegre...")
df_poa = df[df["CODMUNRES"] == COD_MUNICIPIO_POA].copy()
print(f"      Registros de Porto Alegre: {len(df_poa):,}")
print(
    f"      Percentual sobre o Brasil: "
    f"{100 * len(df_poa) / len(df):.2f}%"
)

# Reorganizar colunas na ordem do anteprojeto
df_poa = df_poa[colunas_existentes]

# Etapa 4: Salvar CSV filtrado
print(f"\n[4/4] Salvando CSV filtrado em: {ARQUIVO_DESTINO}")
df_poa.to_csv(ARQUIVO_DESTINO, index=False, encoding="utf-8", sep=";")
tamanho_mb = os.path.getsize(ARQUIVO_DESTINO) / (1024 * 1024)
print(f"      Arquivo salvo. Tamanho: {tamanho_mb:.2f} MB")

# === RESUMO EXPLORATORIO ===
print("\n" + "=" * 65)
print("RESUMO EXPLORATORIO - PORTO ALEGRE 2023")
print("=" * 65)

print(f"\nTotal de nascimentos: {len(df_poa):,}")

print("\nValores nulos por coluna:")
for col in df_poa.columns:
    nulos = df_poa[col].isna().sum()
    pct = 100 * nulos / len(df_poa)
    print(f"   {col:15s}: {nulos:6,} nulos ({pct:5.2f}%)")

if "PARTO" in df_poa.columns:
    print("\nDistribuicao por tipo de parto:")
    contagem_parto = df_poa["PARTO"].value_counts(dropna=False).sort_index()
    for valor, qtd in contagem_parto.items():
        pct = 100 * qtd / len(df_poa)
        rotulo = {1: "Vaginal", 2: "Cesareo"}.get(valor, "Ignorado/Nulo")
        print(f"   {rotulo:18s} (codigo {valor}): {qtd:6,} ({pct:5.2f}%)")

if "RACACOR" in df_poa.columns:
    print("\nDistribuicao por raca/cor da mae:")
    rotulos_raca = {
        1: "Branca", 2: "Preta", 3: "Amarela",
        4: "Parda", 5: "Indigena"
    }
    contagem_raca = df_poa["RACACOR"].value_counts(dropna=False).sort_index()
    for valor, qtd in contagem_raca.items():
        pct = 100 * qtd / len(df_poa)
        rotulo = rotulos_raca.get(valor, "Ignorado/Nulo")
        print(f"   {rotulo:12s} (codigo {valor}): {qtd:6,} ({pct:5.2f}%)")

print("\n" + "=" * 65)
print("Pronto! Dados de Porto Alegre prontos para carregar no PostgreSQL.")
print("=" * 65)