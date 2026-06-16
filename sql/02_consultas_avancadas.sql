-- ============================================================
-- CONSULTAS AVANCADAS - Projeto Parto POA
-- Cruzamento Relacional Analitico:
-- Taxa de cesarianas agrupada por Raca/Cor da gestante e Escolaridade
--
-- Projeto: Intervencoes Medicas e Desigualdades no Parto
-- Autora:  Marina M. Garramones - UFRGS
-- ============================================================


-- ============================================================
-- CONSULTA 1: Taxa de cesarea por raca/cor (visao geral)
-- ============================================================
SELECT
    CASE g.raca_cor
        WHEN 1 THEN 'Branca'
        WHEN 2 THEN 'Preta'
        WHEN 3 THEN 'Amarela'
        WHEN 4 THEN 'Parda'
        WHEN 5 THEN 'Indigena'
        ELSE 'Ignorado'
    END                                                AS raca_cor,
    COUNT(*)                                           AS total_partos,
    SUM(CASE WHEN np.tipo_parto = 2 THEN 1 ELSE 0 END) AS total_cesareas,
    SUM(CASE WHEN np.tipo_parto = 1 THEN 1 ELSE 0 END) AS total_vaginais,
    ROUND(
        100.0 * SUM(CASE WHEN np.tipo_parto = 2 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                  AS taxa_cesarea_pct
FROM gestante g
JOIN nascimento_parto np ON g.id_gestante = np.id_gestante
WHERE np.tipo_parto IN (1, 2)   -- ignora nulos/desconhecidos
GROUP BY g.raca_cor
ORDER BY taxa_cesarea_pct DESC;


-- ============================================================
-- CONSULTA 2: Taxa de cesarea por raca/cor x escolaridade
-- (a consulta principal do projeto)
-- ============================================================
SELECT
    CASE g.raca_cor
        WHEN 1 THEN 'Branca'
        WHEN 2 THEN 'Preta'
        WHEN 3 THEN 'Amarela'
        WHEN 4 THEN 'Parda'
        WHEN 5 THEN 'Indigena'
        ELSE 'Ignorado'
    END                                                AS raca_cor,
    CASE g.escolaridade
        WHEN 1 THEN '1 - Nenhuma'
        WHEN 2 THEN '2 - 1 a 3 anos'
        WHEN 3 THEN '3 - 4 a 7 anos'
        WHEN 4 THEN '4 - 8 a 11 anos'
        WHEN 5 THEN '5 - 12 anos ou mais'
        WHEN 9 THEN '9 - Ignorado'
        ELSE 'Sem informacao'
    END                                                AS escolaridade,
    COUNT(*)                                           AS total_partos,
    ROUND(
        100.0 * SUM(CASE WHEN np.tipo_parto = 2 THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                  AS taxa_cesarea_pct
FROM gestante g
JOIN nascimento_parto np ON g.id_gestante = np.id_gestante
WHERE np.tipo_parto IN (1, 2)
  AND g.raca_cor IS NOT NULL
  AND g.escolaridade IS NOT NULL
GROUP BY g.raca_cor, g.escolaridade
HAVING COUNT(*) >= 10   -- ignora grupos com amostra muito pequena
ORDER BY raca_cor, g.escolaridade;


-- ============================================================
-- CONSULTA 3: Idade media e perfil por raca/cor
-- (contexto demografico complementar)
-- ============================================================
SELECT
    CASE g.raca_cor
        WHEN 1 THEN 'Branca'
        WHEN 2 THEN 'Preta'
        WHEN 3 THEN 'Amarela'
        WHEN 4 THEN 'Parda'
        WHEN 5 THEN 'Indigena'
        ELSE 'Ignorado'
    END                                AS raca_cor,
    COUNT(*)                           AS total_gestantes,
    ROUND(AVG(g.idade_mae)::numeric, 1) AS idade_media,
    ROUND(AVG(g.escolaridade)::numeric, 2) AS escolaridade_media
FROM gestante g
WHERE g.raca_cor IS NOT NULL
GROUP BY g.raca_cor
ORDER BY g.raca_cor;