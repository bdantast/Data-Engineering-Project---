import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import threading
from core.database import db
from core.schema_discover import schema_discover
from config import DB_CONFIG, GROQ_API_KEY, OLLAMA_HOST
from ai.groq_client import groq_client
from ai.ollama_client import ollama_client


class SettingsPage(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill=X, padx=15, pady=(15, 10))
        ttk.Label(header, text="Configuracoes", font=("Segoe UI", 16, "bold")).pack(side=LEFT)

        db_frame = ttk.LabelFrame(self, text="Banco de Dados PostgreSQL (Neon)", padding=15)
        db_frame.pack(fill=X, padx=15, pady=5)

        fields_db = [
            ("Host:", "db_host", DB_CONFIG["host"]),
            ("Porta:", "db_port", str(DB_CONFIG["port"])),
            ("Banco:", "db_name", DB_CONFIG["database"]),
            ("Usuario:", "db_user", DB_CONFIG["user"]),
            ("Senha:", "db_password", DB_CONFIG["password"]),
            ("SSL:", "db_ssl", DB_CONFIG["sslmode"]),
        ]
        self.db_entries = {}
        for label_text, key, default in fields_db:
            row = ttk.Frame(db_frame)
            row.pack(fill=X, pady=2)
            ttk.Label(row, text=label_text, width=10, font=("Segoe UI", 10)).pack(side=LEFT)
            entry = ttk.Entry(row, width=50)
            entry.insert(0, default)
            if "password" in key:
                entry.configure(show="*")
            entry.pack(side=LEFT, padx=(5, 0))
            self.db_entries[key] = row

        btn_row = ttk.Frame(db_frame)
        btn_row.pack(fill=X, pady=(10, 0))
        ttk.Button(btn_row, text="Testar Conexao", bootstyle="info",
                   command=self._test_connection, width=18).pack(side=LEFT, padx=(0, 10))
        ttk.Button(btn_row, text="Descobrir Tabelas", bootstyle="success",
                   command=self._discover_schema, width=18).pack(side=LEFT)

        ai_frame = ttk.LabelFrame(self, text="Inteligencia Artificial", padding=15)
        ai_frame.pack(fill=X, padx=15, pady=5)

        groq_row = ttk.Frame(ai_frame)
        groq_row.pack(fill=X, pady=2)
        ttk.Label(groq_row, text="Groq API Key:", width=14, font=("Segoe UI", 10)).pack(side=LEFT)
        self.groq_entry = ttk.Entry(groq_row, width=50, show="*")
        self.groq_entry.insert(0, GROQ_API_KEY)
        self.groq_entry.pack(side=LEFT, padx=(5, 0))

        ollama_row = ttk.Frame(ai_frame)
        ollama_row.pack(fill=X, pady=2)
        ttk.Label(ollama_row, text="Ollama Host:", width=14, font=("Segoe UI", 10)).pack(side=LEFT)
        self.ollama_entry = ttk.Entry(ollama_row, width=50)
        self.ollama_entry.insert(0, OLLAMA_HOST)
        self.ollama_entry.pack(side=LEFT, padx=(5, 0))

        ai_btn_row = ttk.Frame(ai_frame)
        ai_btn_row.pack(fill=X, pady=(10, 0))
        ttk.Button(ai_btn_row, text="Testar Groq", bootstyle="info",
                   command=self._test_groq, width=15).pack(side=LEFT, padx=(0, 5))
        ttk.Button(ai_btn_row, text="Testar Ollama", bootstyle="info",
                   command=self._test_ollama, width=15).pack(side=LEFT)

        info_frame = ttk.LabelFrame(self, text="Status do Sistema", padding=15)
        info_frame.pack(fill=X, padx=15, pady=5)

        self.status_text = ttk.ScrolledText(info_frame, height=8, state=DISABLED, font=("Consolas", 9))
        self.status_text.pack(fill=X)

        self._update_status()

    def _test_connection(self):
        self.status_var = ttk.StringVar(value="Testando conexao...")
        self._update_status_text("Testando conexao com PostgreSQL...")
        threading.Thread(target=self._test_conn_async, daemon=True).start()

    def _test_conn_async(self):
        try:
            config = self._get_db_config()
            test_db = db.__class__(config)
            ok, msg = test_db.test_connection()
            if ok:
                self.after(0, lambda: self._update_status_text(f"Conexao OK: {msg}"))
            else:
                self.after(0, lambda: self._update_status_text(f"Falha: {msg}"))
        except Exception as e:
            self.after(0, lambda: self._update_status_text(f"Erro: {e}"))

    def _discover_schema(self):
        self._update_status_text("Descobrindo tabelas...")
        threading.Thread(target=self._discover_async, daemon=True).start()

    def _discover_async(self):
        try:
            config = self._get_db_config()
            db.config = config
            db.connect()
            schema_discover.discover()
            tables = schema_discover.tables
            lines = [f"Tabelas encontradas: {len(tables)}"]
            for t in tables:
                cols = schema_discover.schema_info.get(t, [])
                col_names = [c["column_name"] for c in cols]
                lines.append(f"  - {t}: {', '.join(col_names[:8])}{'...' if len(col_names) > 8 else ''}")
            self.after(0, lambda: self._update_status_text("\n".join(lines)))
        except Exception as e:
            self.after(0, lambda: self._update_status_text(f"Erro: {e}"))

    def _test_groq(self):
        key = self.groq_entry.get().strip()
        if not key:
            messagebox.showwarning("Aviso", "Insira uma chave de API Groq")
            return
        groq_client.api_key = key
        self._update_status_text("Testando Groq...")
        threading.Thread(target=self._test_groq_async, daemon=True).start()

    def _test_groq_async(self):
        try:
            ok = groq_client.is_available()
            msg = "Groq OK - API funcionando!" if ok else "Groq indisponivel - verifique a chave"
            self.after(0, lambda: self._update_status_text(msg))
        except Exception as e:
            self.after(0, lambda: self._update_status_text(f"Erro Groq: {e}"))

    def _test_ollama(self):
        host = self.ollama_entry.get().strip()
        ollama_client.host = host
        ok = ollama_client.is_available()
        msg = "Ollama OK - Rodando localmente!" if ok else "Ollama indisponivel - inicie com 'ollama serve'"
        self._update_status_text(msg)

    def _get_db_config(self):
        return {
            "host": self.db_entries["db_host"].winfo_children()[1].get(),
            "port": int(self.db_entries["db_port"].winfo_children()[1].get() or "5432"),
            "database": self.db_entries["db_name"].winfo_children()[1].get(),
            "user": self.db_entries["db_user"].winfo_children()[1].get(),
            "password": self.db_entries["db_password"].winfo_children()[1].get(),
            "sslmode": self.db_entries["db_ssl"].winfo_children()[1].get(),
        }

    def _update_status(self):
        lines = ["=== Status do Sistema ===", ""]
        lines.append(f"PostgreSQL: {'Conectado' if db.connected else 'Desconectado'}")
        lines.append(f"Tabelas: {len(schema_discover.tables)}")
        lines.append(f"Groq API: {'Configurado' if GROQ_API_KEY else 'Nao configurado'}")
        lines.append(f"Ollama: {'Disponivel' if ollama_client.is_available() else 'Indisponivel'}")
        self._update_status_text("\n".join(lines))

    def _update_status_text(self, text):
        self.status_text.configure(state=NORMAL)
        self.status_text.delete("1.0", END)
        self.status_text.insert("1.0", text)
        self.status_text.configure(state=DISABLED)
