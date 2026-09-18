import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
from ui.widgets.ai_chat import AIChatWidget
from core.schema_discover import schema_discover
from core.kpi_engine import kpi_engine
from ai.analyzer import ai_analyzer
from ai.groq_client import groq_client
from ai.ollama_client import ollama_client


class AIAnalysisPage(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.last_analysis = ""
        self._build_ui()

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill=X, padx=15, pady=(15, 5))
        ttk.Label(header, text="Analise com Inteligencia Artificial", font=("Segoe UI", 16, "bold")).pack(side=LEFT)

        status_frame = ttk.Frame(header)
        status_frame.pack(side=RIGHT)
        groq_ok = bool(groq_client.api_key)
        ollama_ok = ollama_client.is_available()
        provider = "Groq" if groq_ok else ("Ollama" if ollama_ok else "Nenhum")
        provider_color = "success" if (groq_ok or ollama_ok) else "danger"
        ttk.Label(status_frame, text=f"IA: {provider}", font=("Segoe UI", 9), bootstyle=provider_color).pack(side=RIGHT)

        preset_frame = ttk.Frame(self)
        preset_frame.pack(fill=X, padx=15, pady=5)
        ttk.Label(preset_frame, text="Analises Pre-definidas:", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 10))

        presets = [
            ("Resumo Executivo", "resumo"),
            ("Analise de Vendas", "vendas"),
            ("Analise Financeira", "financeiro"),
            ("Oportunidades", "oportunidades"),
            ("Problemas e Riscos", "problemas"),
        ]
        for label, key in presets:
            ttk.Button(
                preset_frame,
                text=label,
                bootstyle="outline-info",
                command=lambda k=key: self._run_preset(k),
                width=18,
            ).pack(side=LEFT, padx=2)

        self.auto_btn = ttk.Button(
            preset_frame,
            text="Analise Automatica",
            bootstyle="success",
            command=self._run_auto_analysis,
            width=18,
        )
        self.auto_btn.pack(side=LEFT, padx=5)

        self.result_text = ttk.ScrolledText(
            self,
            height=25,
            state=DISABLED,
            font=("Consolas", 10),
            wrap=WORD,
        )
        self.result_text.pack(fill=BOTH, expand=True, padx=15, pady=5)

        self.chat = AIChatWidget(self, on_send=self._on_chat_send)
        self.chat.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))

        self.status_var = ttk.StringVar(value="Pronto")

    def _run_preset(self, prompt_key):
        self._set_result("Processando analise...")
        threading.Thread(target=self._preset_async, args=(prompt_key,), daemon=True).start()

    def _preset_async(self, prompt_key):
        try:
            result, provider = ai_analyzer.analyze_with_prompt(prompt_key)
            self.last_analysis = result
            self.after(0, lambda: self._set_result(f"[via {provider}]\n\n{result}"))
        except Exception as e:
            self.after(0, lambda: self._set_result(f"Erro: {e}"))

    def _run_auto_analysis(self):
        self._set_result("Executando analise automatica completa...")
        self.auto_btn.configure(state=DISABLED)
        threading.Thread(target=self._auto_async, daemon=True).start()

    def _auto_async(self):
        try:
            result, provider = ai_analyzer.auto_analyze()
            self.last_analysis = result
            self.after(0, lambda: self._set_result(f"[via {provider}]\n\n{result}"))
        except Exception as e:
            self.after(0, lambda: self._set_result(f"Erro: {e}"))
        finally:
            self.after(0, lambda: self.auto_btn.configure(state=NORMAL))

    def _on_chat_send(self, question):
        try:
            response, provider = ai_analyzer.ask(question)
            return f"[via {provider}]\n\n{response}"
        except Exception as e:
            return f"Erro: {e}"

    def _set_result(self, text):
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", text)
        self.result_text.configure(state=DISABLED)
