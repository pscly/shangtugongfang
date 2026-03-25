from app.core.config import get_settings


class MattingProvider:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_url = settings.matting_api_url
        self.api_key = settings.matting_api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_url and self.api_key)
