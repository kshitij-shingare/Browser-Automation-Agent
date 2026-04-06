from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    groq_api_key: str = ""
    google_api_key: str = ""
    default_llm: Literal["groq", "gemini"] = "groq"
    groq_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    gemini_model: str = "gemini-2.0-flash"
    use_vision: bool = False
    output_dir: str = "outputs"
    log_dir: str = "logs"
    max_steps: int = 50
