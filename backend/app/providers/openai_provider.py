from openai import AsyncOpenAI

from app.core.config import get_settings


class OpenAIProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    @property
    def configured(self) -> bool:
        return self.client is not None
