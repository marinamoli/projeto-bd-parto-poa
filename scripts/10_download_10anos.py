"""
Download em lote dos microdados do SINASC de 2014 a 2023 (10 anos).
Faz download sequencial, descompacta cada ZIP e remove o original
para economizar espaco em disco.

Tempo estimado: 30-60 minutos.
Espaco em disco necessario: ~10 GB temporarios.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import os
import urllib.request
import zipfile
import time

PASTA_DESTINO = "dados"
os.makedirs(PASTA_DESTINO, exist_ok=True)

ANOS = list(range(2014, 2024))  # 2014, 2015, ..., 2023
URL_BASE = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINASC/csv/SINASC_{ano}_csv.zip"


def baixar_arquivo(url, destino, ano):
    def reporthook(bloco, tam_bloco, tam_total):
        if tam_total > 0:
            baixado_mb = (bloco * tam_bloco) / 1024 / 1024
            total_mb = tam_total / 1024 / 1024
            pct = min(100, (bloco * tam_bloco / tam_total) * 100)
            print(f"\r   [{ano}] {pct:5.1f}% ({baixado_mb:6.1f} MB / {total_mb:6.1f} MB)",
                  end="", flush=True)
    urllib.request.urlretrieve(url, destino, reporthook=reporthook)
    print()


def descompactar(arquivo_zip, pasta_destino):
    with zipfile.ZipFile(arquivo_zip, "r") as zf:
        zf.extractall(pasta_destino)
        nomes = zf.namelist()
    return nomes


print("=" * 65)
print("Download em lote SINASC 2014-2023 (10 anos)")
print("=" * 65)

inicio_total = time.time()
sucessos = []
falhas = []

for ano in ANOS:
    print(f"\n>>> Ano {ano}")
    url = URL_BASE.format(ano=ano)
    arquivo_zip = os.path.join(PASTA_DESTINO, f"SINASC_{ano}.zip")
    arquivo_csv = os.path.join(PASTA_DESTINO, f"SINASC_{ano}.csv")

    if os.path.exists(arquivo_csv):
        tamanho_mb = os.path.getsize(arquivo_csv) / 1024 / 1024
        print(f"   Ja existe: {arquivo_csv} ({tamanho_mb:.1f} MB) - pulando.")
        sucessos.append(ano)
        continue

    try:
        print(f"   URL: {url}")
        baixar_arquivo(url, arquivo_zip, ano)
        print(f"   Descompactando...")
        nomes = descompactar(arquivo_zip, PASTA_DESTINO)
        print(f"   Extraido: {nomes}")
        os.remove(arquivo_zip)
        print(f"   ZIP removido.")
        tamanho_mb = os.path.getsize(arquivo_csv) / 1024 / 1024
        print(f"   OK: {arquivo_csv} ({tamanho_mb:.1f} MB)")
        sucessos.append(ano)
    except Exception as e:
        print(f"\n   ERRO no ano {ano}: {e}")
        falhas.append(ano)
        if os.path.exists(arquivo_zip):
            os.remove(arquivo_zip)
        continue

duracao_min = (time.time() - inicio_total) / 60

print("\n" + "=" * 65)
print("RESUMO DO DOWNLOAD")
print("=" * 65)
print(f"Anos com sucesso: {len(sucessos)}/10")
print(f"   {sucessos}")
if falhas:
    print(f"Anos com falha: {falhas}")
print(f"\nTempo total: {duracao_min:.1f} minutos")

print(f"\nArquivos CSV em {PASTA_DESTINO}/:")
total_mb = 0
for arq in sorted(os.listdir(PASTA_DESTINO)):
    if arq.startswith("SINASC_") and arq.endswith(".csv"):
        caminho = os.path.join(PASTA_DESTINO, arq)
        tam_mb = os.path.getsize(caminho) / 1024 / 1024
        total_mb += tam_mb
        print(f"   {arq}: {tam_mb:.1f} MB")
print(f"\nTotal: {total_mb:.1f} MB ({total_mb/1024:.2f} GB)")

print("\n" + "=" * 65)
print("Proximo passo: rodar 11_filtrar_poa_10anos.py")
print("=" * 65)