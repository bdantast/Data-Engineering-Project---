# DataPulse - Business Intelligence Desktop

> Software de analise e dashboard para bancos de dados PostgreSQL com inteligencia artificial integrada.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20Tech-336791?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)

## Visao Geral

O **DataPulse** e um software desktop de Business Intelligence desenvolvido em Python que conecta-se a qualquer banco de dados PostgreSQL (incluindo Neon Tech), analisa automaticamente os dados e gera dashboards interativos com KPIs, graficos e analises por inteligencia artificial.

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
git clone https://github.com/bdantast/datapulse-business-intelligence.git
cd datapulse-business-intelligence

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

# O DataPulse detecta automaticamente
```

## Estrutura do Projeto

```
DataPulse/
├── main.py                    # Entry point
├── config.py                  # Configuracoes
├── requirements.txt           # Dependencias
├── .env.example               # Template de configuracao
├── ui/                        # Interface grafica
│   ├── app.py                 # Janela principal
│   ├── pages/                 # Paginas do dashboard
│   │   ├── dashboard.py       # Visao geral
│   │   ├── vendas.py          # Analise de vendas
│   │   ├── financeiro.py      # Analise financeira
│   │   ├── ai_analysis.py     # Analise com IA
│   │   ├── export.py          # Exportacao
│   │   └── settings.py        # Configuracoes
│   └── widgets/               # Componentes reutilizaveis
│       ├── kpi_card.py        # Cards de KPI
│       ├── chart_frame.py     # Frames de graficos
│       ├── data_table.py      # Tabelas de dados
│       └── ai_chat.py         # Chat com IA
├── core/                      # Logica de negocio
│   ├── database.py            # Conexao PostgreSQL
│   ├── schema_discover.py     # Auto-descoberta
│   ├── kpi_engine.py          # Calculo de KPIs
│   └── charts.py              # Geracao de graficos
├── ai/                        # Integracao IA
│   ├── groq_client.py         # Cliente Groq
│   ├── ollama_client.py       # Cliente Ollama
│   ├── analyzer.py            # Orquestrador
│   └── prompts.py             # Templates
└── export/                    # Exportacao
    ├── pdf_report.py          # Geracao PDF
    ├── excel_report.py        # Geracao Excel
    ├── email_sender.py        # Envio por email
    ├── share.py               # WhatsApp/Telegram
    └── printer.py             # Impressao
```

## Uso

1. **Conectar ao Banco**: Va em Configuracoes e conecte-se ao seu PostgreSQL
2. **Descobrir Tabelas**: Clique em "Descobrir Tabelas" para analise automatica
3. **Explorar Dashboard**: Navegue pelas paginas para ver KPIs e graficos
4. **Analise com IA**: Use a aba "Analise IA" para insights automatizados
5. **Exportar**: Gere relatorios PDF/Excel ou compartilhe via email/WhatsApp

## Licenca

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autor

**bdantast** - [GitHub](https://github.com/bdantast)

---

Desenvolvido como projeto de portfolio em Data Engineering e Business Intelligence.
