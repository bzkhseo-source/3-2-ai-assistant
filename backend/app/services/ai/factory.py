import os
from app.services.ai.base import AIProvider


def get_ai_provider() -> AIProvider:
    provider = os.getenv("AI_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from app.services.ai.gemini_provider import GeminiProvider
        return GeminiProvider()
    elif provider == "openai":
        from app.services.ai.openai_provider import OpenAIProvider
        return OpenAIProvider()
    else:
        raise ValueError(f"지원하지 않는 AI_PROVIDER 값입니다: {provider}")