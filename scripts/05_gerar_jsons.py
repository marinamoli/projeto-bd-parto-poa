"""
Script para gerar documentos JSON simulando relatorios da SMS-POA
para cada Distrito Sanitario.

Os dados sao plausiveis e baseados em padroes documentados em
boletins oficiais da Prefeitura de Porto Alegre, mas constituem
SIMULACAO para validacao da arquitetura hibrida.

Projeto: Intervencoes Medicas e Desigualdades no Parto
Autora: Marina M. Garramones - UFRGS
"""

import json
import os

PASTA_DESTINO = "dados/relatorios_json"
os.makedirs(PASTA_DESTINO, exist_ok=True)

# Os 8 Distritos Sanitarios de Porto Alegre com perfis socioeconomicos
# baseados em dados publicos da SMS-POA e do Censo IBGE
distritos = [
    {
        "id": "DS001",
        "nome": "Centro",
        "perfil_socioeconomico": "alto",
        "populacao_estimada": 280000,
        "infraestrutura": {
            "leitos_obstetricos": 78,
            "salas_parto_normal": 4,
            "centro_cirurgico_24h": True,
            "uti_neonatal": True,
            "avaliacao_geral": "adequada"
        },
        "indicadores": {
            "taxa_cesarea_distrito": 58.4,
            "cobertura_prenatal_7_consultas": 81.2,
            "mortalidade_infantil_por_mil": 7.8,
            "proporcao_maes_negras_pct": 18.5
        },
        "observacoes": "Distrito com maior concentracao de hospitais privados. Tendencia historica a cesareas eletivas."
    },
    {
        "id": "DS002",
        "nome": "Norte",
        "perfil_socioeconomico": "medio",
        "populacao_estimada": 215000,
        "infraestrutura": {
            "leitos_obstetricos": 32,
            "salas_parto_normal": 2,
            "centro_cirurgico_24h": True,
            "uti_neonatal": False,
            "avaliacao_geral": "adequada"
        },
        "indicadores": {
            "taxa_cesarea_distrito": 47.2,
            "cobertura_prenatal_7_consultas": 74.5,
            "mortalidade_infantil_por_mil": 9.4,
            "proporcao_maes_negras_pct": 26.3
        },
        "observacoes": "Distrito misto, com predominio de classe media."
    },
    {
        "id": "DS003",
        "nome": "Noroeste",
        "perfil_socioeconomico": "alto",
        "populacao_estimada": 165000,
        "infraestrutura": {
            "leitos_obstetricos": 45,
            "salas_parto_normal": 3,
            "centro_cirurgico_24h": True,
            "uti_neonatal": True,
            "avaliacao_geral": "adequada"
        },
        "indicadores": {
            "taxa_cesarea_distrito": 62.7,
            "cobertura_prenatal_7_consultas": 84.6,
            "mortalidade_infantil_por_mil": 6.5,
            "proporcao_maes_negras_pct": 14.2
        },
        "observacoes": "Distrito predominantemente branco e de alta renda."
    },
    {
        "id": "DS004",
        "nome": "Leste",
        "perfil_socioeconomico": "medio_baixo",
        "populacao_estimada": 195000,
        "infraestrutura": {
            "leitos_obstetricos": 28,
            "salas_parto_normal": 2,
            "centro_cirurgico_24h": False,
            "uti_neonatal": False,
            "avaliacao_geral": "parcial"
        },
        "indicadores": {
            "taxa_cesarea_distrito": 41.8,
            "cobertura_prenatal_7_consultas": 68.3,
            "mortalidade_infantil_por_mil": 11.2,
            "proporcao_maes_negras_pct": 35.7
        },
        "observacoes": "Distrito com lacunas na cobertura de cirurgia 24h. Demanda reprimida."
    },
    {
        "id": "DS005",
        "nome": "Gloria-Cruzeiro-Cristal",
        "perfil_socioeconomico": "medio_baixo",
        "populacao_estimada": 175000,
        "infraestrutura": {
            "leitos_obstetricos": 22,
            "salas_parto_normal": 2,
            "centro_cirurgico_24h": True,
            "uti_neonatal": False,
            "avaliacao_geral": "parcial"
        },
        "indicadores": {
            "taxa_cesarea_distrito": 38.5,
            "cobertura_prenatal_7_consultas": 66.1,
            "mortalidade_infantil_por_mil": 10.8,
            "proporcao_maes_negras_pct": 41.6
        },
        "observacoes": "Alta proporcao de gestantes negras. UTI neonatal ausente."
    },
    {
        "id": "DS006",
        "nome": "Partenon-Lomba do Pinheiro",
        "perfil_socioeconomico": "baixo",
        "populacao_estimada": 230000,
        "infraestrutura": {
            "leitos_obstetricos": 20,
            "salas_parto_normal": 2,
            "centro_cirurgico_24h": False,
            "uti_neonatal": False,
            "avaliacao_geral": "inadequada"
        },
        "indicadores": {
            "taxa_cesarea_distrito": 34.2,
            "cobertura_prenatal_7_consultas": 61.4,
            "mortalidade_infantil_por_mil": 13.7,
            "proporcao_maes_negras_pct": 42.9
        },
        "observacoes": "Distrito de alta vulnerabilidade social. Infraestrutura obstetrica deficitaria."
    },
    {
        "id": "DS007",
        "nome": "Restinga-Extremo Sul",
        "perfil_socioeconomico": "baixo",
        "populacao_estimada": 145000,
        "infraestrutura": {
            "leitos_obstetricos": 14,
            "salas_parto_normal": 1,
            "centro_cirurgico_24h": False,
            "uti_neonatal": False,
            "avaliacao_geral": "inadequada"
        },
        "indicadores": {
            "taxa_cesarea_distrito": 31.6,
            "cobertura_prenatal_7_consultas": 57.8,
            "mortalidade_infantil_por_mil": 15.2,
            "proporcao_maes_negras_pct": 47.8
        },
        "observacoes": "Maior taxa de mortalidade infantil da cidade. Maior proporcao de maes negras."
    },
    {
        "id": "DS008",
        "nome": "Sul-Centro Sul",
        "perfil_socioeconomico": "medio",
        "populacao_estimada": 200000,
        "infraestrutura": {
            "leitos_obstetricos": 35,
            "salas_parto_normal": 2,
            "centro_cirurgico_24h": True,
            "uti_neonatal": True,
            "avaliacao_geral": "adequada"
        },
        "indicadores": {
            "taxa_cesarea_distrito": 49.3,
            "cobertura_prenatal_7_consultas": 75.2,
            "mortalidade_infantil_por_mil": 9.1,
            "proporcao_maes_negras_pct": 24.5
        },
        "observacoes": "Distrito misto com cobertura adequada."
    }
]

# Salvar cada distrito como um arquivo JSON individual
print("Gerando documentos JSON...")
for d in distritos:
    nome_arquivo = f"relatorio_{d['id']}_{d['nome'].lower().replace(' ', '_').replace('-', '_')}.json"
    caminho = os.path.join(PASTA_DESTINO, nome_arquivo)

    documento = {
        "tipo_documento": "relatorio_indicadores_distrito",
        "fonte": "Secretaria Municipal de Saude de Porto Alegre (SIMULADO)",
        "data_referencia": "2023-12-31",
        "distrito_sanitario": d["nome"],
        "id_distrito": d["id"],
        "perfil_socioeconomico": d["perfil_socioeconomico"],
        "populacao_estimada": d["populacao_estimada"],
        "infraestrutura": d["infraestrutura"],
        "indicadores": d["indicadores"],
        "observacoes": d["observacoes"],
        "metadados": {
            "versao": "1.0",
            "autor": "Marina M. Garramones (simulacao academica)",
            "projeto": "Intervencoes Medicas e Desigualdades no Parto"
        }
    }

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(documento, f, ensure_ascii=False, indent=2)

    print(f"   Criado: {nome_arquivo}")

print(f"\n{len(distritos)} documentos JSON gerados em: {PASTA_DESTINO}/")