"""Carrega configurações do ambiente.

- Prioriza variáveis do sistema.
- Se existir um arquivo configs/.env, carrega via python-dotenv.
"""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env se existir
ENV_PATH = Path(__file__).resolve().parents[1] / "configs" / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
XAI_API_KEY: str | None = os.getenv("XAI_API_KEY")  # Nova API key para Grok
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")  # Nova API key para Groq
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
SONAR_API_KEY: str | None = os.getenv("SONAR_API_KEY")
SONAR_API_BASE: str = os.getenv("SONAR_API_BASE", "https://api.perplexity.ai")
SONAR_DEFAULT_MODEL: str = os.getenv("SONAR_DEFAULT_MODEL", "sonar-pro")

# Configurações LLM Provider
DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "google_gemini")
DEFAULT_GOOGLE_MODEL: str = os.getenv("DEFAULT_GOOGLE_MODEL", "gemini-2.0-flash")
DEFAULT_GROK_MODEL: str = os.getenv("DEFAULT_GROK_MODEL", "grok-beta")
DEFAULT_GROQ_MODEL: str = os.getenv("DEFAULT_GROQ_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1000"))

# Validações leves (opcionalmente tornar estritas em produção)
REQUIRED_ON_RUNTIME = [
    ("SUPABASE_URL", SUPABASE_URL),
    ("SUPABASE_KEY", SUPABASE_KEY),
]

missing = [name for name, val in REQUIRED_ON_RUNTIME if not val]
if missing:
    # Evita quebrar import em ambientes de desenvolvimento; logue um aviso
    import warnings
    warnings.warn(f"Variáveis ausentes: {', '.join(missing)}. Configure configs/.env ou variáveis de ambiente.")

# Configurações de banco (Postgres/Supabase)
DB_HOST: str | None = os.getenv("DB_HOST")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_NAME: str | None = os.getenv("DB_NAME")
DB_USER: str | None = os.getenv("DB_USER")
DB_PASSWORD: str | None = os.getenv("DB_PASSWORD")

def build_db_dsn() -> str:
    """Monta DSN para conexão psycopg.

    Exemplo: postgresql://user:pass@host:5432/dbname
    """
    user = DB_USER or "postgres"
    host = DB_HOST or "localhost"
    name = DB_NAME or "postgres"
    port = DB_PORT or "5432"
    password = DB_PASSWORD or ""
    if password:
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return f"postgresql://{user}@{host}:{port}/{name}"
