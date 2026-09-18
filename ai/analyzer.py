from ai.groq_client import groq_client
from ai.ollama_client import ollama_client
from ai.prompts import ANALYSIS_SYSTEM_PROMPT, DATA_SUMMARY_TEMPLATE, QUESTION_PROMPTS
from core.database import db
from core.schema_discover import schema_discover
from core.kpi_engine import kpi_engine


class AIAnalyzer:
    def __init__(self):
        self.preferred_provider = "groq"

    def _build_data_summary(self, table=None):
        tables = [table] if table else schema_discover.tables
        summaries = []
        for t in tables:
            info = schema_discover.schema_info.get(t, [])
            kpis = kpi_engine.kpis.get(t, {})
            resumo = kpis.get("resumo", {})
            vendas = kpis.get("vendas", {})
            cols = ", ".join([c["column_name"] for c in info[:15]])
            metrics_lines = []
            for key, val in vendas.items():
                if key.startswith("colunas_"):
                    continue
                if isinstance(val, (int, float)):
                    metrics_lines.append(f"- {key}: {val:,.2f}")
                elif isinstance(val, str) and val:
                    metrics_lines.append(f"- {key}: {val}")
            categories = vendas.get("top_categorias", [])
            cat_text = ""
            if categories:
                cat_text = "\n".join([
                    f"- {c.get('categoria', 'N/A')}: {c.get('total', 0):,.2f}"
                    for c in categories[:10]
                ])
            else:
                cat_text = "Nenhuma categoria detectada automaticamente."
            summary = DATA_SUMMARY_TEMPLATE.format(
                table=t,
                total_rows=resumo.get("total_registros", 0),
                first_date=vendas.get("primeira_data", "N/A"),
                last_date=vendas.get("ultima_data", "N/A"),
                columns=cols,
                metrics="\n".join(metrics_lines) if metrics_lines else "Nenhuma metrica calculada.",
                categories=cat_text,
            )
            summaries.append(summary)
        return "\n---\n".join(summaries)

    def _call_ai(self, messages, max_tokens=2048):
        if self.preferred_provider == "groq" and groq_client.api_key:
            try:
                return groq_client.chat(messages, max_tokens=max_tokens), "Groq"
            except Exception:
                pass
        if ollama_client.is_available():
            try:
                return ollama_client.chat(messages), "Ollama"
            except Exception:
                pass
        if groq_client.api_key:
            try:
                return groq_client.chat(messages, max_tokens=max_tokens), "Groq"
            except Exception as e:
                raise RuntimeError(f"Nenhuma IA disponivel. Groq: {e}")
        raise RuntimeError(
            "Nenhuma IA disponivel. Configure GROQ_API_KEY no .env ou instale Ollama."
        )

    def ask(self, question, table=None):
        data_summary = self._build_data_summary(table)
        system_msg = {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT}
        user_msg = {"role": "user", "content": f"## Dados:\n{data_summary}\n\n## Pergunta:\n{question}"}
        response, provider = self._call_ai([system_msg, user_msg])
        return response, provider

    def auto_analyze(self, table=None):
        data_summary = self._build_data_summary(table)
        system_msg = {
            "role": "system",
            "content": (
                "Voce é um analista de dados senior. Analise automaticamente os dados fornecidos "
                "e gere um relatorio completo em portugues com: 1) Resumo Executivo, "
                "2) KPIs Principais, 3) Tendencias Identificadas, 4) Problemas ou Anomalias, "
                "5) Recomendacoes de Acao. Use markdown格式, titulos, listas e tabelas."
            ),
        }
        user_msg = {"role": "user", "content": f"## Dados do Banco para Analise Automatica:\n{data_summary}"}
        response, provider = self._call_ai([system_msg, user_msg], max_tokens=4096)
        return response, provider

    def analyze_with_prompt(self, prompt_key, table=None):
        question = QUESTION_PROMPTS.get(prompt_key, QUESTION_PROMPTS["resumo"])
        return self.ask(question, table)


ai_analyzer = AIAnalyzer()
