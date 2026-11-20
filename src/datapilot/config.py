"""Settings from .env. Secrets never live in code."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = ROOT / "runs"
SAMPLE_CSV = ROOT / "sample_data" / "sales_2026.csv"

# provider -> (default model, base_url, env key)
PROVIDERS = {
    "groq": ("openai/gpt-oss-120b", "https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "openrouter": ("meta-llama/llama-3.3-70b-instruct", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "openai": ("gpt-4o-mini", None, "OPENAI_API_KEY"),
}
UI_PROVIDERS = list(PROVIDERS)  # mock is test/offline only


@dataclass(frozen=True)
class Settings:
    provider: str = "mock"
    model: str = ""
    api_key: str = ""
    temperature: float = 0.1
    max_messages: int = 20
    executor: str = "local"
    exec_timeout: int = 60

    @property
    def is_mock(self) -> bool:
        return self.provider == "mock"

    @property
    def ready(self) -> bool:
        return self.is_mock or bool(self.api_key)


def load_settings(provider: str | None = None, model: str | None = None) -> Settings:
    load_dotenv(ROOT / ".env", override=True)
    prov = (provider or os.getenv("LLM_PROVIDER", "mock")).lower()
    key = os.getenv(PROVIDERS[prov][2], "") if prov in PROVIDERS else ""
    return Settings(
        provider=prov,
        model=model or os.getenv("LLM_MODEL", ""),
        api_key=key,
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        max_messages=int(os.getenv("MAX_MESSAGES", "20")),
        executor=os.getenv("EXECUTOR", "local").lower(),
        exec_timeout=int(os.getenv("EXEC_TIMEOUT", "60")),
    )
