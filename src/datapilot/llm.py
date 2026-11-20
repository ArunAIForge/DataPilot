"""Model factory: the only module that picks the LLM client. Providers: openrouter, groq, openai."""
from __future__ import annotations

from .config import PROVIDERS, Settings


def build_client(settings: Settings, role: str = "", mock_script=None):
    if settings.is_mock:
        from autogen_ext.models.replay import ReplayChatCompletionClient
        return ReplayChatCompletionClient(list((mock_script or {}).get(role, ["MOCK"])))

    from autogen_core.models import ModelInfo
    from autogen_ext.models.openai import OpenAIChatCompletionClient

    default_model, base_url, _ = PROVIDERS[settings.provider]
    kwargs = dict(
        model=settings.model or default_model,
        api_key=settings.api_key,
        temperature=settings.temperature,
    )
    if base_url:  # Groq / OpenRouter speak the OpenAI protocol but AutoGen needs model capabilities declared
        kwargs["base_url"] = base_url
        kwargs["model_info"] = ModelInfo(
            vision=False, function_calling=True, json_output=False, family="unknown", structured_output=False
        )
    return OpenAIChatCompletionClient(**kwargs)
