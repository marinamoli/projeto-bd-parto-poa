"""
Filtra os 10 CSVs do SINASC (2014-2023) para Porto Alegre.
Versao ROBUSTA: normaliza nomes de colunas (alguns anos vem em minusculas),
detecta separador/encoding e tolera anos com formato divergente.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import pandas as pd
import os
import time

PASTA_DADOS = "dados"
ARQUIVO_SAIDA = os.path.join(PASTA_DADOS, "sinasc_poa_2014_2023.csv")

COD_POA = 431490

COLUNAS_PROJETO = [
    "IDADEMAE", "RACACOR", "ESCMAE", "CODMUNRES",
    "PARTO", "TPROBSON", "STTRABPART"
]

ANOS = list(range(2014, 2024))


def ler_csv_robusto(arquivo):
    """Le CSV com detecao automatica e normalizacao de nomes de colunas."""
    for encoding in ["latin-1", "utf-8"]:
        try:
            df_header = pd.read_csv(arquivo, sep=";", encoding=encoding, nrows=0)
            colunas_originais = list(df_header.columns)
            colunas_upper = [c.upper() for c in colunas_originais]

            if "CODMUNRES" not in colunas_upper:
                continue

            mapa_colunas = {orig: orig.upper() for orig in colunas_originais}
            colunas_disponiveis_originais = [
                orig for orig in colunas_originais
                if orig.upper() in COLUNAS_PROJETO
            ]

            df = pd.read_csv(
                arquivo, sep=";", encoding=encoding,
                usecols=colunas_disponiveis_originais, low_memory=False
            )
            df.rename(columns=mapa_colunas, inplace=True)
            return df, None

        except UnicodeDecodeError:
            continue
        except Exception as e:
            return None, str(e)

    return None, "Nao foi possivel ler com latin-1 nem utf-8"


print("=" * 65)
print("Filtragem SINASC 2014-2023 -> Porto Alegre")
print("Versao robusta com normalizacao de nomes")
print("=" * 65)

dfs_poa = []
inicio = time.time()
anos_sucesso = []
anos_falha = []

for ano in ANOS:
    arquivo = os.path.join(PASTA_DADOS, f"SINASC_{ano}.csv")

    if not os.path.exists(arquivo):
        print(f"\n[{ano}] AVISO: arquivo nao encontrado, pulando.")
        anos_falha.append((ano, "arquivo nao existe"))
        continue

    print(f"\n[{ano}] Lendo {arquivo}...")
    t0 = time.time()

    df_ano, erro = ler_csv_robusto(arquivo)

    if df_ano is None:
        print(f"   FALHA: {erro}")
        anos_falha.append((ano, erro))
        continue

    print(f"   Linhas Brasil: {len(df_ano):,}")
    print(f"   Colunas disponiveis: {sorted(df_ano.columns.tolist())}")

    df_poa = df_ano[df_ano["CODMUNRES"] == COD_POA].copy()

    for col in COLUNAS_PROJETO:
        if col not in df_poa.columns:
            df_poa[col] = None

    df_poa["ANO"] = ano

    print(f"   Linhas POA:    {len(df_poa):,}")

    if len(df_poa) > 0:
        dfs_poa.append(df_poa)
        anos_sucesso.append(ano)
    else:
        anos_falha.append((ano, "0 linhas para POA"))

    duracao = time.time() - t0
    print(f"   Tempo: {duracao:.1f}s")

if not dfs_poa:
    print("\nERRO: Nenhum ano foi processado com sucesso!")
    raise SystemExit(1)

print("\n" + "=" * 65)
print("Concatenando todos os anos com sucesso...")

colunas_finais = COLUNAS_PROJETO + ["ANO"]
dfs_poa = [df[colunas_finais] for df in dfs_poa]
df_final = pd.concat(dfs_poa, ignore_index=True)
print(f"Total POA: {len(df_final):,} nascimentos")

print(f"\nSalvando em {ARQUIVO_SAIDA}...")
df_final.to_csv(ARQUIVO_SAIDA, sep=";", index=False, encoding="utf-8")
tamanho_mb = os.path.getsize(ARQUIVO_SAIDA) / 1024 / 1024
print(f"Tamanho: {tamanho_mb:.2f} MB")

duracao_total = (time.time() - inicio) / 60
print("\n" + "=" * 65)
print("RESUMO FINAL")
print("=" * 65)

print(f"\nAnos com sucesso: {len(anos_sucesso)} -> {anos_sucesso}")
if anos_falha:
    print(f"\nAnos com falha:")
    for ano, motivo in anos_falha:
        print(f"   {ano}: {motivo}")

print("\nDistribuicao por ano:")
for ano, total in df_final.groupby("ANO").size().items():
    print(f"   {ano}: {total:,}")

print("\nDistribuicao por tipo de parto:")
for tipo, total in df_final.groupby("PARTO").size().items():
    pct = 100 * total / len(df_final)
    nome = {1.0: "Vaginal", 2.0: "Cesareo"}.get(tipo, "Ignorado")
    print(f"   {nome}: {total:,} ({pct:.2f}%)")

print("\nDistribuicao por raca/cor:")
nomes_raca = {1.0: "Branca", 2.0: "Preta", 3.0: "Amarela", 4.0: "Parda", 5.0: "Indigena"}
for raca, total in df_final.groupby("RACACOR").size().items():
    pct = 100 * total / len(df_final)
    nome = nomes_raca.get(raca, "Ignorado")
    print(f"   {nome}: {total:,} ({pct:.2f}%)")

print(f"\nTempo total: {duracao_total:.1f} minutos")
print("=" * 65)