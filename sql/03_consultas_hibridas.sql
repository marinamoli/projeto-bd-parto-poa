-- ============================================================
-- CONSULTAS HIBRIDAS SQL + JSONB
-- Demonstram a integracao entre modelo relacional e NoSQL
-- usando operadores nativos do PostgreSQL (->, ->>)
--
-- Projeto: Intervencoes Medicas e Desigualdades no Parto
-- Autora:  Marina M. Garramones - UFRGS
-- ============================================================


-- ============================================================
-- CONSULTA HIBRIDA 1: Indicadores por distrito sanitario
-- Demonstra extracao de dados do JSONB usando -> e ->>
-- ============================================================
SELECT
    conteudo_jsonb->>'distrito_sanitario'                          AS distrito,
    conteudo_jsonb->>'perfil_socioeconomico'                       AS perfil,
    (conteudo_jsonb->'indicadores'->>'taxa_cesarea_distrito')::numeric    AS taxa_cesarea_distrito,
    (conteudo_jsonb->'indicadores'->>'mortalidade_infantil_por_mil')::numeric AS mort_infantil,
    (conteudo_jsonb->'indicadores'->>'proporcao_maes_negras_pct')::numeric AS pct_maes_negras,
    conteudo_jsonb->'infraestrutura'->>'avaliacao_geral'           AS infraestrutura
FROM relatorios_municipais
WHERE conteudo_jsonb->>'tipo_documento' = 'relatorio_indicadores_distrito'
ORDER BY (conteudo_jsonb->'indicadores'->>'mortalidade_infantil_por_mil')::numeric DESC;


-- ============================================================
-- CONSULTA HIBRIDA 2: Comparacao da taxa REAL com SINASC
-- Cruza o dado relacional (SINASC) com o dado oficial (JSONB)
-- ============================================================
WITH taxa_real_sinasc AS (
    SELECT
        ROUND(
            100.0 * SUM(CASE WHEN np.tipo_parto = 2 THEN 1 ELSE 0 END)
            / COUNT(*), 2
        ) AS taxa_cesarea_calculada,
        COUNT(*) AS total_partos
    FROM nascimento_parto np
    WHERE np.tipo_parto IN (1, 2)
)
SELECT
    'Taxa de cesarea (SINASC 2023 - relacional)'      AS fonte,
    tr.taxa_cesarea_calculada                          AS valor,
    '%'                                                AS unidade,
    tr.total_partos                                    AS amostra
FROM taxa_real_sinasc tr

UNION ALL

SELECT
    'Taxa de mortalidade infantil (Boletim SMS-POA 2022 - NoSQL)' AS fonte,
    (rm.conteudo_jsonb->'indicadores_principais'->>'taxa_mortalidade_infantil_por_mil')::numeric AS valor,
    'por mil nasc. vivos'                              AS unidade,
    NULL                                               AS amostra
FROM relatorios_municipais rm
WHERE rm.conteudo_jsonb->>'natureza_dados' LIKE '%REAL%';


-- ============================================================
-- CONSULTA HIBRIDA 3: Distritos criticos (do JSONB) 
-- cruzados com perfil sociodemografico real (do SINASC)
-- A consulta hibrida mais poderosa do projeto
-- ============================================================
SELECT
    rm.conteudo_jsonb->>'distrito_sanitario'           AS distrito,
    (rm.conteudo_jsonb->'indicadores'->>'mortalidade_infantil_por_mil')::numeric AS mort_infantil_jsonb,
    (rm.conteudo_jsonb->'indicadores'->>'proporcao_maes_negras_pct')::numeric    AS pct_maes_negras_jsonb,
    rm.conteudo_jsonb->'infraestrutura'->>'avaliacao_geral'        AS infraestrutura,
    rm.conteudo_jsonb->>'perfil_socioeconomico'                    AS perfil,
    -- Subconsulta: numero total de partos no SINASC (modelo relacional)
    (SELECT COUNT(*) FROM nascimento_parto)            AS total_partos_sinasc
FROM relatorios_municipais rm
WHERE rm.conteudo_jsonb->>'tipo_documento' = 'relatorio_indicadores_distrito'
  AND (rm.conteudo_jsonb->'infraestrutura'->>'avaliacao_geral') IN ('inadequada', 'parcial')
ORDER BY mort_infantil_jsonb DESC;


-- ============================================================
-- CONSULTA HIBRIDA 4: Busca no JSONB usando @>
-- Demonstra outro operador NoSQL: contencao
-- ============================================================
SELECT
    conteudo_jsonb->>'distrito_sanitario'              AS distrito,
    conteudo_jsonb->>'observacoes'                     AS observacoes
FROM relatorios_municipais
WHERE conteudo_jsonb @> '{"perfil_socioeconomico": "baixo"}'::jsonb;