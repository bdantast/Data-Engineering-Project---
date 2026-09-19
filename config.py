import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "neondb"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "sslmode": os.getenv("DB_SSL", "require"),
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "user": os.getenv("SMTP_USER", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
}

APP_NAME = "Data Engineering"
APP_VERSION = "1.0.0"
APP_THEME = "darkly"

COLORS = {
    "bg_dark": "#0a0e17",
    "bg_card": "#111827",
    "bg_sidebar": "#0d1117",
    "bg_table": "#1a1f2e",
    "bg_table_alt": "#151b2b",
    "border": "#1e293b",
    "neon_blue": "#00d4ff",
    "neon_green": "#00ff88",
    "neon_purple": "#a855f7",
    "neon_pink": "#f472b6",
    "neon_orange": "#fb923c",
    "neon_yellow": "#facc15",
    "text_primary": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "success": "#00ff88",
    "danger": "#ff4444",
    "warning": "#facc15",
    "info": "#00d4ff",
}
