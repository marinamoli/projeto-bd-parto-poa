-- ============================================================
-- CONSULTAS BASICAS - Projeto Parto POA
-- Implementacao das consultas previstas na secao 5.1 do
-- anteprojeto. Validacao da arquitetura hibrida.
--
-- Projeto: Intervencoes Medicas e Desigualdades no Parto
-- Autora:  Marina M. Garramones - UFRGS
-- ============================================================


-- ============================================================
-- CONSULTA BASICA 1: Contagem de intervencoes (partos por tipo)
-- Objetivo: numero total de partos no SINASC 2023 por tipo
-- (vaginal vs cesareo) com percentual sobre o total.
-- ============================================================
SELECT
    CASE tipo_parto
        WHEN 1 THEN 'Vaginal'
        WHEN 2 THEN 'Cesareo'
        ELSE 'Ignorado'
    END                                                    AS tipo_parto,
    COUNT(*)                                               AS total,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    )                                                      AS percentual
FROM nascimento_parto
GROUP BY tipo_parto
ORDER BY total DESC;


-- ============================================================
-- CONSULTA BASICA 2: Filtro demografico
-- Objetivo: nascimentos por faixa etaria da mae e escolaridade.
-- Cruza duas variaveis sociodemograficas da gestante.
-- ============================================================
SELECT
    CASE
        WHEN g.idade_mae < 20                THEN '1 - Menor de 20'
        WHEN g.idade_mae BETWEEN 20 AND 29   THEN '2 - 20 a 29 anos'
        WHEN g.idade_mae BETWEEN 30 AND 39   THEN '3 - 30 a 39 anos'
        WHEN g.idade_mae >= 40               THEN '4 - 40 anos ou mais'
        ELSE 'Sem informacao'
    END                                                    AS faixa_etaria,
    CASE g.escolaridade
        WHEN 1 THEN 'Nenhuma'
        WHEN 2 THEN '1-3 anos'
        WHEN 3 THEN '4-7 anos'
        WHEN 4 THEN '8-11 anos'
        WHEN 5 THEN '12+ anos'
        ELSE 'Sem informacao'
    END                                                    AS escolaridade,
    COUNT(*)                                               AS total_nascimentos
FROM gestante g
WHERE g.idade_mae IS NOT NULL
  AND g.escolaridade IS NOT NULL
GROUP BY faixa_etaria, escolaridade, g.escolaridade
ORDER BY faixa_etaria, g.escolaridade;


-- ============================================================
-- CONSULTA BASICA 3: Mapeamento espacial
-- Objetivo: distribuicao de nascimentos por municipio de
-- residencia da gestante. Filtra apenas Porto Alegre,
-- conforme escopo do projeto.
-- ============================================================
SELECT
    g.cod_municipio                                        AS codigo_ibge,
    CASE g.cod_municipio
        WHEN '431490' THEN 'Porto Alegre'
        ELSE 'Outro municipio'
    END                                                    AS municipio,
    COUNT(*)                                               AS total_nascimentos,
    ROUND(AVG(g.idade_mae)::numeric, 1)                    AS idade_media_mae,
    ROUND(AVG(g.escolaridade)::numeric, 2)                 AS escolaridade_media
FROM gestante g
GROUP BY g.cod_municipio
ORDER BY total_nascimentos DESC;


-- ============================================================
-- CONSULTA BASICA 4: Busca em documentos NoSQL (JSONB)
-- Objetivo: extrair indicadores especificos dos relatorios
-- municipais usando operadores nativos do PostgreSQL (->, ->>).
-- ============================================================
SELECT
    conteudo_jsonb->>'distrito_sanitario'                  AS distrito_sanitario,
    conteudo_jsonb->>'perfil_socioeconomico'               AS perfil,
    (conteudo_jsonb->'indicadores'->>'taxa_cesarea_distrito')::numeric   AS taxa_cesarea_pct,
    (conteudo_jsonb->'indicadores'->>'cobertura_prenatal_7_consultas')::numeric AS cobertura_prenatal_pct,
    conteudo_jsonb->'infraestrutura'->>'avaliacao_geral'   AS infraestrutura,
    (conteudo_jsonb->'infraestrutura'->>'leitos_obstetricos')::integer   AS leitos_obstetricos
FROM relatorios_municipais
WHERE conteudo_jsonb->>'tipo_documento' = 'relatorio_indicadores_distrito'
ORDER BY taxa_cesarea_pct DESC;