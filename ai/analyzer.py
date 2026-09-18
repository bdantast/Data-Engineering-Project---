from ai.groq_client import groq_client
from ai.ollama_client import ollama_client
from ai.prompts import ANALYSIS_SYSTEM_PROMPT, DATA_SUMMARY_TEMPLATE, QUESTION_PROMPTS
from core.database import db
from core.schema_discover import schema_discover
from core.kpi_engine import kpi_engine
from core.security import mask_dataframe, mask_dict_list


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
            if categories:
                masked_cats = mask_dict_list(categories)
                cat_text = "\n".join([
                    f"- {c.get('categoria', 'N/A')}: {c.get('total', 0):,.2f}"
                    for c in masked_cats[:10]
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

    def _send_sample_to_ai(self, table):
        try:
            df = schema_discover.get_table_preview(table, limit=20)
            if df.empty:
                return ""
            df_masked = mask_dataframe(df)
            lines = [f"Amstra de dados (mascarada LGPD) da tabela '{t}':"]
            for _, row in df_masked.iterrows():
                vals = [f"{k}={v}" for k, v in row.items() if str(v).strip()]
                lines.append("  " + ", ".join(vals[:8]))
            return "\n".join(lines)
        except Exception:
            return ""

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
        sample_text = ""
        if table:
            sample_text = self._send_sample_to_ai(table)
        elif schema_discover.tables:
            sample_text = self._send_sample_to_ai(schema_discover.tables[0])
        full_context = data_summary
        if sample_text:
            full_context += f"\n\n{sample_text}"
        system_msg = {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT}
        user_msg = {
            "role": "user",
            "content": (
                f"## Dados:\n{full_context}\n\n"
                f"IMPORTANTE: Os dados acima foram mascarados para protecao de privacidade (LGPD). "
                f"Analise apenas os valores numericos e estruturas.\n\n"
                f"## Pergunta:\n{question}"
            ),
        }
        response, provider = self._call_ai([system_msg, user_msg])
        return response, provider

    def auto_analyze(self, table=None):
        data_summary = self._build_data_summary(table)
        sample_text = ""
        if table:
            sample_text = self._send_sample_to_ai(table)
        elif schema_discover.tables:
            for t in schema_discover.tables[:3]:
                s = self._send_sample_to_ai(t)
                if s:
                    sample_text += s + "\n\n"
        full_context = data_summary
        if sample_text:
            full_context += f"\n\n{sample_text}"
        system_msg = {
            "role": "system",
            "content": (
                "Voce e um analista de dados senior. Analise automaticamente os dados fornecidos "
                "e gere um relatorio completo em portugues com: 1) Resumo Executivo, "
                "2) KPIs Principais, 3) Tendencias Identificadas, 4) Problemas ou Anomalias, "
                "5) Recomendacoes de Acao. Use markdown, titulos, listas e tabelas. "
                "IMPORTANTE: Os dados foram mascarados para protecao LGPD. Analise apenas "
                "valores numericos e estruturas, sem tentar revelar dados pessoais."
            ),
        }
        user_msg = {
            "role": "user",
            "content": f"## Dados do Banco para Analise Automatica:\n{full_context}",
        }
        response, provider = self._call_ai([system_msg, user_msg], max_tokens=4096)
        return response, provider

    def analyze_with_prompt(self, prompt_key, table=None):
        question = QUESTION_PROMPTS.get(prompt_key, QUESTION_PROMPTS["resumo"])
        return self.ask(question, table)


ai_analyzer = AIAnalyzer()
