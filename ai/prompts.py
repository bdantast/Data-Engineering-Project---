ANALYSIS_SYSTEM_PROMPT = """Voce é um analista de dados business intelligence senior com expertise em:
- Analise financeira (margens, fluxo de caixa, ROI, break-even)
- Analise de vendas (tendencias, sazonalidade, performance por regiao/produto)
- KPIs administrativos e operacionais
- Identificacao de anomalias e oportunidades

Responda sempre em portugues brasileiro. Use markdown com:
- Titulos para cada secao
- Listas com bullets para insights
- Tabela quando apropriado
- Destaque para numeros importantes
- Recomendacoes accionaveis no final
"""

DATA_SUMMARY_TEMPLATE = """
## Tabela: {table}
- Total de registros: {total_rows}
- Periodo: {first_date} ate {last_date}
- Colunas detectadas: {columns}

### Principais Metricas:
{metrics}

### Top Categorias:
{categories}
"""

QUESTION_PROMPTS = {
    "resumo": "Faca um resumo executivo dos dados mostrando os principais numeros e tendencias.",
    "vendas": "Analise as vendas em detalhe: tendencias, sazonalidade, melhores e piores performadores.",
    "financeiro": "Analise a situacao financeira: margens, custos, lucratividade e pontos de atencao.",
    "oportunidades": "Identifique oportunidades de crescimento e melhoria baseado nos dados.",
    "problemas": "Identifique problemas, anomalias ou riscos nos dados que precisam de atencao.",
    "previsao": "Com base nos dados historicos, faca uma previsao e sugira planos de acao.",
}
