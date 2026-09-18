import requests
from config import OLLAMA_HOST, OLLAMA_MODEL


class OllamaClient:
    def __init__(self, host=None, model=None):
        self.host = host or OLLAMA_HOST
        self.model = model or OLLAMA_MODEL

    def chat(self, messages, temperature=0.3):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            resp = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]
        except requests.ConnectionError:
            raise ConnectionError(
                "Ollama nao esta rodando. Inicie com 'ollama serve' ou instale em ollama.com"
            )
        except Exception as e:
            raise RuntimeError(f"Erro ao comunicar com Ollama: {e}")

    def analyze_data(self, data_summary, question):
        messages = [
            {
                "role": "system",
                "content": (
                    "Voce é um analista de dados expert. Analise os dados fornecidos e responda "
                    "de forma clara, objetiva e com insights accionaveis. Use formatacao markdown."
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
                    "Voce é um analista de dados senior. Analise automaticamente os dados fornecidos "
                    "e gere um relatorio completo com: 1) Resumo executivo, 2) KPIs principais, "
                    "3) Tendencias, 4) Problemas, 5) Recomendacoes. Use markdown."
                ),
            },
            {
                "role": "user",
                "content": f"## Dados para Analise Automatica:\n{data_summary}",
            },
        ]
        return self.chat(messages, temperature=0.2)

    def is_available(self):
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False


ollama_client = OllamaClient()
