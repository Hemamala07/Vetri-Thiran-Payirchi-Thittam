from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True

    # AI mode:
    # cloud = use Gemini + Hugging Face
    # mock = run without API keys
    ai_mode: str = "cloud"

    # Gemini
    gemini_api_key: str = ""
    gemini_outline_model: str = "gemini-3.8-flash"
    gemini_story_model: str = "gemini-3.1-pro-preview"

    # Hugging Face
    hf_token: str = ""
    image_provider: str = "hf"
    hf_image_model: str = "stabilityai/stable-diffusion-3.5-large"
    hf_provider: str = "auto"

    # Local Diffusers
    local_image_model: str = "stabilityai/stable-diffusion-3.5-large"
    local_device: str = "auto"

    # Comic settings
    panel_count: int = 5
    image_width: int = 768
    image_height: int = 512
    max_story_prompt_length: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def templates_dir(self) -> Path:
        return BASE_DIR / "templates"

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "static"

    @property
    def panel_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def export_dir(self) -> Path:
        return self.static_dir / "exports"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    settings.panel_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.export_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return settings