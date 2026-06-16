"""
Script de download dos microdados do SINASC - Ano 2023.
Fonte: Portal de Dados Abertos do SUS / Ministério da Saúde
Projeto: Intervenções Médicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import urllib.request
import zipfile
import os

# Configurações
URL_SINASC = (
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br"
    "/SINASC/csv/SINASC_2023_csv.zip"
)
PASTA_DADOS = "dados"
ARQUIVO_ZIP = os.path.join(PASTA_DADOS, "SINASC_2023.zip")

# Criar pasta de dados se não existir
os.makedirs(PASTA_DADOS, exist_ok=True)

print("=" * 65)
print("Download dos Microdados do SINASC - Ano 2023")
print("Fonte: Portal de Dados Abertos do SUS / Ministério da Saúde")
print("=" * 65)
print(f"\nURL:     {URL_SINASC}")
print(f"Destino: {ARQUIVO_ZIP}\n")

# Função para mostrar progresso do download
def progresso(bloco, tamanho_bloco, tamanho_total):
    baixado = bloco * tamanho_bloco
    if tamanho_total > 0:
        percentual = min(100, baixado * 100 / tamanho_total)
        mb_baixado = baixado / (1024 * 1024)
        mb_total = tamanho_total / (1024 * 1024)
        print(
            f"\rProgresso: {percentual:5.1f}% "
            f"({mb_baixado:7.1f} MB / {mb_total:7.1f} MB)",
            end="",
        )

# Download
print("Iniciando download (pode levar alguns minutos)...\n")
try:
    urllib.request.urlretrieve(URL_SINASC, ARQUIVO_ZIP, reporthook=progresso)
    tamanho_mb = os.path.getsize(ARQUIVO_ZIP) / (1024 * 1024)
    print(f"\n\nDownload concluido. Tamanho: {tamanho_mb:.1f} MB")
except Exception as e:
    print(f"\n\nErro no download: {e}")
    raise SystemExit(1)

# Descompactacao
print("\nDescompactando arquivo ZIP...")
try:
    with zipfile.ZipFile(ARQUIVO_ZIP, "r") as zip_ref:
        arquivos_dentro = zip_ref.namelist()
        print(f"   Arquivos no ZIP: {arquivos_dentro}")
        zip_ref.extractall(PASTA_DADOS)
    print(f"Arquivos extraidos em: {PASTA_DADOS}/")
except Exception as e:
    print(f"Erro na descompactacao: {e}") 
    raise SystemExit(1)

# Limpar o ZIP para economizar espaco
try:
    os.remove(ARQUIVO_ZIP)
    print("ZIP removido (economia de espaco).")
except Exception:
    pass

# Listar arquivos finais na pas