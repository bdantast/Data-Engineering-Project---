# Data Engineering - Business Intelligence Desktop

> Software de analise e dashboard para bancos de dados PostgreSQL com inteligencia artificial integrada.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20Tech-336791?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)

## Visao Geral

O **Data Engineering** e um software desktop de Business Intelligence desenvolvido em Python que conecta-se a qualquer banco de dados PostgreSQL (incluindo Neon Tech), analisa automaticamente os dados e gera dashboards interativos com KPIs, graficos e analises por inteligencia artificial.

## Funcionalidades

### Dashboard Interativo
- KPIs automaticos (Receita, Margem, Ticket Medio, Crescimento)
- Graficos de tendencia, distribuicao e comparativo
- Tabelas de dados com ordenacao e filtragem
- Descoberta automatica de tabelas e colunas

### Analise de Vendas
- Tendencia de vendas por periodo
- Vendas por categoria/produto/vendedor
- Comparativo entre periodos
- KPIs: Receita bruta, liquida, ticket medio, descontos

### Analise Financeira
- Composicao de receita vs custos
- Margem de lucro operacional
- Fluxo de caixa
- Break-even analysis

### Inteligencia Artificial
- **Groq API** (cloud) - Gratuito, 14.400 req/dia, ultra rapido
- **Ollama** (local) - Offline, sem limite, privado
- Analise automatica completa dos dados
- Chat interativo para perguntas sobre os dados
- Analises pre-definidas: resumo, vendas, financeiro, oportunidades, riscos

### Exportacao e Compartilhamento
- **PDF**: Relatorio completo com graficos e KPIs
- **Excel**: Planilha com multiplas abas e formatacao
- **Email**: Envio direto via SMTP
- **WhatsApp**: Deep link com resumo formatado
- **Telegram**: Compartilhamento via deep link
- **Impressao**: Impressao direta do relatorio

## Stack Tecnologica

| Camada | Tecnologia |
|---|---|
| Interface | Python + ttkbootstrap |
| Banco de Dados | PostgreSQL (Neon Tech) via psycopg2 |
| Graficos | Matplotlib |
| IA (Cloud) | Groq API (Llama 3.3 70B) |
| IA (Local) | Ollama (Llama 3.2) |
| PDF | ReportLab |
| Excel | OpenPyXL |
| Email | smtplib (Python nativo) |

## Instalacao

### Pre-requisitos
- Python 3.10 ou superior
- pip
- Conta no [Neon Tech](https://neon.tech) (PostgreSQL serverless - free tier)
- API Key do [Groq](https://console.groq.com) (gratuita, sem cartao de credito)

### Passo a passo

```bash
# 1. Clone o repositorio
git clone https://github.com/bdantast/Data Engineering-business-intelligence.git
cd Data Engineering-business-intelligence

# 2. Instale as dependencias
python setup.py

# 3. Configure o arquivo .env
copy .env.example .env
# Edite .env com suas credenciais do Neon Tech e Groq

# 4. Execute o programa
python main.py
```

## Configuracao

### Neon Tech (PostgreSQL)
1. Acesse [console.neon.tech](https://console.neon.tech)
2. Crie um projeto
3. Copie a string de conexao para o arquivo `.env`

### Groq API (IA Gratuita)
1. Acesse [console.groq.com](https://console.groq.com)
2. Crie uma conta (sem cartao de credito)
3. Gere uma API Key
4. Adicione no arquivo `.env` como `GROQ_API_KEY=sua_chave_aqui`

### Ollama (IA Local - Opcional)
```bash
# Instale o Ollama
# Windows: https://ollama.com/download

# Baixe um modelo
ollama pull llama3.2

# O Data Engineering detecta automaticamente
```

## Estrutura do Projeto

```
Data Engineering/
â”œâ”€â”€ main.py                    # Entry point
â”œâ”€â”€ config.py                  # Configuracoes
â”œâ”€â”€ requirements.txt           # Dependencias
â”œâ”€â”€ .env.example               # Template de configuracao
â”œâ”€â”€ ui/                        # Interface grafica
â”‚   â”œâ”€â”€ app.py                 # Janela principal
â”‚   â”œâ”€â”€ pages/                 # Paginas do dashboard
â”‚   â”‚   â”œâ”€â”€ dashboard.py       # Visao geral
â”‚   â”‚   â”œâ”€â”€ vendas.py          # Analise de vendas
â”‚   â”‚   â”œâ”€â”€ financeiro.py      # Analise financeira
â”‚   â”‚   â”œâ”€â”€ ai_analysis.py     # Analise com IA
â”‚   â”‚   â”œâ”€â”€ export.py          # Exportacao
â”‚   â”‚   â””â”€â”€ settings.py        # Configuracoes
â”‚   â””â”€â”€ widgets/               # Componentes reutilizaveis
â”‚       â”œâ”€â”€ kpi_card.py        # Cards de KPI
â”‚       â”œâ”€â”€ chart_frame.py     # Frames de graficos
â”‚       â”œâ”€â”€ data_table.py      # Tabelas de dados
â”‚       â””â”€â”€ ai_chat.py         # Chat com IA
â”œâ”€â”€ core/                      # Logica de negocio
â”‚   â”œâ”€â”€ database.py            # Conexao PostgreSQL
â”‚   â”œâ”€â”€ schema_discover.py     # Auto-descoberta
â”‚   â”œâ”€â”€ kpi_engine.py          # Calculo de KPIs
â”‚   â””â”€â”€ charts.py              # Geracao de graficos
â”œâ”€â”€ ai/                        # Integracao IA
â”‚   â”œâ”€â”€ groq_client.py         # Cliente Groq
â”‚   â”œâ”€â”€ ollama_client.py       # Cliente Ollama
â”‚   â”œâ”€â”€ analyzer.py            # Orquestrador
â”‚   â””â”€â”€ prompts.py             # Templates
â””â”€â”€ export/                    # Exportacao
    â”œâ”€â”€ pdf_report.py          # Geracao PDF
    â”œâ”€â”€ excel_report.py        # Geracao Excel
    â”œâ”€â”€ email_sender.py        # Envio por email
    â”œâ”€â”€ share.py               # WhatsApp/Telegram
    â””â”€â”€ printer.py             # Impressao
```

## Uso

1. **Conectar ao Banco**: Va em Configuracoes e conecte-se ao seu PostgreSQL
2. **Descobrir Tabelas**: Clique em "Descobrir Tabelas" para analise automatica
3. **Explorar Dashboard**: Navegue pelas paginas para ver KPIs e graficos
4. **Analise com IA**: Use a aba "Analise IA" para insights automatizados
5. **Exportar**: Gere relatorios PDF/Excel ou compartilhe via email/WhatsApp

## Seguranca (Cybersecurity E2E)

O Data Engineering implementa as melhores praticas de seguranca de ponta a ponta:

### Protecao contra SQL Injection
- Todas as queries usam `psycopg2.sql.Identifier` para nomes de tabelas/colunas
- Validacao de identificadores com regex e whitelist de keywords SQL
- Nenhum f-string com dados do usuario em queries SQL

### LGPD - Protecao de Dados Pessoais
- Mascaramento automatico de PII antes de enviar dados para IA
- Deteccao e redacao de: CPF, CNPJ, email, telefone, cartao, CEP
- DataFrames mascarados antes de qualquer envio externo

### Criptografia e Conexao Segura
- SSL obrigatorio (`sslmode=require`) em todas conexoes PostgreSQL
- Comunicacao HTTPS com APIs (Groq, Ollama)
- Armazenamento seguro de credenciais via DPAPI Windows

### Validacao de Integridade
- Hash SHA-256 disponibilizado para validacao do executavel
- CodeQL workflow para analise SAST automatica

### Boas Practicas
- Credenciais nunca no codigo-fonte (apenas em `.env`)
- `.gitignore` protege arquivos sensiveis
- Recomendacao de usuario somente-leitura no PostgreSQL

### Configuracao Segura do PostgreSQL
```sql
-- Crie um usuario apenas para leitura
CREATE USER usuario_analitico WITH PASSWORD 'senha_forte';
GRANT CONNECT ON DATABASE meu_banco TO usuario_analitico;
GRANT USAGE ON SCHEMA public TO usuario_analitico;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO usuario_analitico;
```

## Licenca

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autor

**bdantast** - [GitHub](https://github.com/bdantast)

---

Desenvolvido como projeto de portfolio em Data Engineering e Business Intelligence.
