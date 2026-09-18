from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


class GroqClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or GROQ_API_KEY
        self.model = GROQ_MODEL
        self._client = None

    def _get_client(self):
        if self._client is None:
            if not self.api_key:
                raise ValueError("Chave da API Groq nao configurada. Configure GROQ_API_KEY no .env")
            self._client = Groq(api_key=self.api_key)
        return self._client

    def chat(self, messages, temperature=0.3, max_tokens=2048):
        client = self._get_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def analyze_data(self, data_summary, question):
        messages = [
            {
                "role": "system",
                "content": (
                    "Voce é um analista de dados expert. Analise os dados fornecidos e responda "
                    "de forma clara, objetiva e com insights accionaveis. Use formatacao markdown. "
                    "Quando possivel, sugira acoes especificas baseadas nos dados."
                ),
            },
            {
                "role": "user",
                "content": f"## Dados do Banco:\n{data_summary}\n\n## Pergunta:\n{question}",
            },
        ]
        return self.chat(messages)

    def auto_analyze(self, data_summary):
        messages = [
            {
                "role": "system",
                "content": (
                    "Voce é um analista de dados senior. Analise automaticamente os dados fornecidos e gere "
                    "um relatorio completo com: 1) Resumo executivo, 2) KPIs principais, 3) Tendencias "
                    "identificadas, 4) Problemas ou anomalias, 5) Recomendacoes de acao. "
                    "Use markdown com titulos, listas e formatacao clara."
                ),
            },
            {
                "role": "user",
                "content": f"## Dados do Banco para Analise Automatica:\n{data_summary}",
            },
        ]
        return self.chat(messages, max_tokens=4096)

    def is_available(self):
        try:
            if not self.api_key:
                return False
            client = self._get_client()
            client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
            )
            return True
        except Exception:
            return False


groq_client = GroqClient()
