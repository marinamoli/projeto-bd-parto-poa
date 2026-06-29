---

## 🚀 Como Executar Localmente

```bash
# 1. Clonar repositório
git clone https://github.com/marinamoli/projeto-bd-parto-poa.git
cd projeto-bd-parto-poa

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar .env com credenciais PostgreSQL
echo "DB_NAME=postgres
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432" > .env

# 4. Executar dashboard
python -m streamlit run dashboard_app.py
```

---

## 📊 Funcionalidades do Dashboard

O dashboard interativo oferece 5 abas de análise:

1. **Achados Principais** — Gráfico da paradoxo de Simpson (Raça × Escolaridade × Taxa Cesárea)
2. **Evolução Temporal** — Tendências 2014-2023 (nascimentos e cesárea)
3. **Análise Demográfica** — Distribuição por raça, idade e escolaridade
4. **Distritos Sanitários** — Mapa interativo com os 8 distritos de POA + indicadores extraídos do JSONB
5. **Arquitetura** — Documentação técnica do projeto

**Filtros disponíveis**: período temporal, raça/cor, faixa etária, escolaridade.

---

## 📚 Trabalhos Relacionados

O projeto se posiciona na intersecção de três eixos:

- **Médico-epidemiológico**: Souza et al. (2021), Racismo Obstétrico (2024)
- **Técnico / Engenharia de Dados**: PCDaS/Fiocruz (Elasticsearch), Pegasus/TCU (PostgreSQL)
- **Geográfico-territorial**: Ribeiro et al. (2023) sobre disparidades em POA

---

## 📄 Fontes de Dados

- [SINASC — Sistema de Informações sobre Nascidos Vivos (DATASUS)](https://datasus.saude.gov.br/transferencia-de-arquivos/)
- [Boletim do Comitê de Prevenção do Óbito Infantil — SMS-POA](https://prefeitura.poa.br/sms)

---

## 📜 Licença

Projeto acadêmico — INF01006 UFRGS, 2026.