-- ============================================================
-- MIGRACAO DO ESQUEMA: adicionar coluna ANO
-- ============================================================
-- Objetivo: estender o esquema relacional para suportar
-- analise temporal de 10 anos (2014-2023).
--
-- Projeto: Intervencoes Medicas e Desigualdades no Parto
-- Autora:  Marina M. Garramones - UFRGS
-- ============================================================


-- 1. Limpa dados antigos (vamos recarregar com 10 anos)
TRUNCATE TABLE nascimento_parto, gestante RESTART IDENTITY CASCADE;


-- 2. Adiciona coluna ANO em nascimento_parto
ALTER TABLE nascimento_parto
ADD COLUMN IF NOT EXISTS ano INTEGER;


-- 3. Restricao: ano deve estar entre 2014 e 2023
ALTER TABLE nascimento_parto
ADD CONSTRAINT chk_ano_valido
CHECK (ano BETWEEN 2014 AND 2023);


-- 4. Indice para acelerar consultas por ano
CREATE INDEX IF NOT EXISTS idx_nascimento_parto_ano
ON nascimento_parto(ano);


-- 5. Comentario na coluna
COMMENT ON COLUMN nascimento_parto.ano IS
'Ano de referencia do nascimento (SINASC). Valores aceitos: 2014-2023.';


-- ============================================================
-- VERIFICACAO
-- ============================================================
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'nascimento_parto'
ORDER BY ordinal_position;