-- ============================================================
-- ESQUEMA DO BANCO DE DADOS - PROJETO PARTO POA
-- Arquitetura Hibrida: Relacional + NoSQL (JSONB)
--
-- Projeto: Intervencoes Medicas e Desigualdades no Parto
-- Autora:  Marina M. Garramones - UFRGS
-- Fonte:   SINASC 2023 (DATASUS) + Relatorios SMS-POA
-- ============================================================

-- Limpeza previa (para reexecucao do script sem erros)
DROP TABLE IF EXISTS nascimento_parto CASCADE;
DROP TABLE IF EXISTS gestante CASCADE;
DROP TABLE IF EXISTS relatorios_municipais CASCADE;

-- ============================================================
-- TABELA 1: GESTANTE
-- Armazena os dados sociodemograficos da mae
-- ============================================================
CREATE TABLE gestante (
    id_gestante      SERIAL       PRIMARY KEY,
    idade_mae        INTEGER,
    raca_cor         INTEGER,     -- 1=Branca, 2=Preta, 3=Amarela, 4=Parda, 5=Indigena
    escolaridade     INTEGER,     -- Anos de estudo
    cod_municipio    VARCHAR(7)   -- Codigo IBGE do municipio de residencia

    -- Restricoes de dominio
    , CONSTRAINT chk_raca_cor    CHECK (raca_cor IS NULL OR raca_cor BETWEEN 1 AND 5)
    , CONSTRAINT chk_idade_mae   CHECK (idade_mae IS NULL OR idade_mae BETWEEN 10 AND 70)
);

COMMENT ON TABLE  gestante              IS 'Dados sociodemograficos das gestantes';
COMMENT ON COLUMN gestante.raca_cor     IS '1=Branca, 2=Preta, 3=Amarela, 4=Parda, 5=Indigena';
COMMENT ON COLUMN gestante.escolaridade IS 'Anos de estudo da mae';

-- ============================================================
-- TABELA 2: NASCIMENTO_PARTO
-- Armazena os dados de cada nascimento/parto
-- Relacionamento N:1 com GESTANTE
-- ============================================================
CREATE TABLE nascimento_parto (
    id_parto              SERIAL       PRIMARY KEY,
    id_gestante           INTEGER      NOT NULL REFERENCES gestante(id_gestante)
                                       ON DELETE CASCADE,
    tipo_parto            INTEGER,     -- 1=Vaginal, 2=Cesareo
    classificacao_robson  INTEGER,     -- Grupo de Robson (1 a 10)
    status_trab_parto     INTEGER      -- 1=Sim, 2=Nao, 3=Nao se aplica

    -- Restricoes de dominio
    , CONSTRAINT chk_tipo_parto CHECK (tipo_parto IS NULL OR tipo_parto IN (1, 2))
);

COMMENT ON TABLE  nascimento_parto                      IS 'Registros de nascimentos e tipos de parto';
COMMENT ON COLUMN nascimento_parto.tipo_parto           IS '1=Vaginal, 2=Cesareo';
COMMENT ON COLUMN nascimento_parto.classificacao_robson IS 'Grupo de Robson (1-10)';

-- Indices para acelerar consultas analiticas
CREATE INDEX idx_nascimento_gestante  ON nascimento_parto(id_gestante);
CREATE INDEX idx_nascimento_tipo      ON nascimento_parto(tipo_parto);
CREATE INDEX idx_gestante_raca        ON gestante(raca_cor);
CREATE INDEX idx_gestante_municipio   ON gestante(cod_municipio);

-- ============================================================
-- TABELA 3: RELATORIOS_MUNICIPAIS (NoSQL via JSONB)
-- Armazena documentos semiestruturados da SMS-POA
-- ============================================================
CREATE TABLE relatorios_municipais (
    id_documento     SERIAL       PRIMARY KEY,
    data_referencia  DATE,
    conteudo_jsonb   JSONB        NOT NULL
);

COMMENT ON TABLE  relatorios_municipais                IS 'Relatorios semiestruturados da SMS-POA (NoSQL)';
COMMENT ON COLUMN relatorios_municipais.conteudo_jsonb IS 'Documento JSON com indicadores por distrito sanitario';

-- Indice GIN para acelerar buscas dentro do JSONB
CREATE INDEX idx_relatorios_jsonb ON relatorios_municipais USING GIN (conteudo_jsonb);

-- ============================================================
-- VERIFICACAO FINAL
-- ============================================================
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns
     WHERE table_name = t.table_name) AS num_colunas
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('gestante', 'nascimento_parto', 'relatorios_municipais')
ORDER BY table_name;