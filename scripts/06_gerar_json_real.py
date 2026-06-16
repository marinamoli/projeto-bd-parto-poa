"""
Script para gerar UM documento JSON REAL baseado em fontes oficiais
da Secretaria Municipal de Saude de Porto Alegre.

Diferente dos 8 documentos simulados, este contem APENAS dados
publicados oficialmente, com referencias verificaveis.

Fonte: Boletim do Comite de Prevencao do Obito Infantil e Fetal
de Porto Alegre, publicado pela SMS-POA em novembro de 2024.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import json
import os

PASTA_DESTINO = "dados/relatorios_json"
os.makedirs(PASTA_DESTINO, exist_ok=True)

# Documento JSON com dados REAIS extraidos de fontes oficiais
documento_real = {
    "tipo_documento": "boletim_mortalidade_infantil",
    "fonte": "Comite de Prevencao do Obito Infantil e Fetal - SMS-POA",
    "fonte_url": "https://prefeitura.poa.br/sms/noticias/boletim-traz-analise-da-mortalidade-infantil-em-porto-alegre",
    "data_publicacao": "2024-11-19",
    "ano_referencia": 2022,
    "natureza_dados": "REAL - dados oficiais publicados",
    "abrangencia": "Municipio de Porto Alegre - RS",

    "indicadores_principais": {
        "taxa_mortalidade_infantil_por_mil": 7.8,
        "unidade": "obitos por 1.000 nascidos vivos",
        "comparativo": {
            "rio_grande_do_sul": 10.46,
            "brasil": 12.60,
            "meta_poa_2025": 8.5
        },
        "tendencia_historica": "queda continua nos ultimos anos, com menores indices em 2020 e 2022"
    },

    "fatores_risco_identificados": {
        "peso_ao_nascer": {
            "descricao": "Bebes nascidos com menos de 2,5 kg apresentam taxa de mortalidade significativamente maior",
            "ano_observacao": 2023
        },
        "escolaridade_materna": {
            "descricao": "Correlacao inversa entre escolaridade materna e mortalidade infantil",
            "fonte_complementar": "Boletim epidemiologico SMS-POA"
        },
        "duracao_gestacao": {
            "descricao": "Prematuridade como fator de risco principal"
        }
    },

    "distritos_criticos": {
        "descricao": "Regioes com maiores coeficientes de mortalidade infantil",
        "lista": ["Cristal", "Cruzeiro", "Extremo-Sul"],
        "observacao": "Necessidade de avaliar acesso aos servicos nestes distritos"
    },

    "principais_causas_obito": {
        "afeccoes_perinatais_e_malformacoes_congenitas": {
            "percentual_aproximado": 80,
            "descricao": "Responsaveis por mais de 80% dos casos de obito infantil"
        }
    },

    "contexto_assistencial": {
        "areas_de_intervencao": [
            "Pre-natal",
            "Atendimento ao parto e nascimento",
            "Seguimento na Atencao Primaria"
        ],
        "comentario_oficial": "Dados refletem esforco continuo em melhorar assistencia desde pre-natal ate seguimento na APS",
        "porta_voz": "Sonia (citada no boletim oficial)"
    },

    "metadados": {
        "versao": "1.0",
        "autor_compilacao": "Marina M. Garramones - UFRGS",
        "projeto": "Intervencoes Medicas e Desigualdades no Parto",
        "observacao_importante": "Este documento integra a arquitetura hibrida do projeto. Os dados sao REAIS e verificaveis, em contraste com os 8 documentos simulados criados para validacao tecnica da arquitetura."
    }
}

# Salvar arquivo
nome_arquivo = "relatorio_REAL_mortalidade_infantil_2022.json"
caminho = os.path.join(PASTA_DESTINO, nome_arquivo)

with open(caminho, "w", encoding="utf-8") as f:
    json.dump(documento_real, f, ensure_ascii=False, indent=2)

print("=" * 65)
print("Documento JSON REAL gerado com sucesso!")
print("=" * 65)
print(f"\nArquivo:  {nome_arquivo}")
print(f"Local:    {PASTA_DESTINO}/")
print(f"Tamanho:  {os.path.getsize(caminho)} bytes")
print(f"\nFonte oficial:")
print(f"  Boletim do Comite de Prevencao do Obito Infantil e Fetal")
print(f"  Secretaria Municipal de Saude de Porto Alegre")
print(f"  Publicado em: Novembro/2024")
print(f"  Ano de referencia dos dados: 2022")
print("\n" + "=" * 65)
print("Estado atual da pasta relatorios_json:")
for arq in sorted(os.listdir(PASTA_DESTINO)):
    if arq.endswith(".json"):
        tipo = "[REAL]" if "REAL" in arq else "[SIMULADO]"
        print(f"  {tipo}  {arq}")
print("=" * 65)