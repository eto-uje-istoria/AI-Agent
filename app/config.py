from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_api_key: str = Field(default="")
    llm_base_url: str = Field(default="")
    llm_model: str = Field(default="")

    tavily_api_key: str = Field(default="")

    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)

    max_tokens: int = Field(default=1024)
    temperature: float = Field(default=0.2)

    data_dir: str = Field(default="./data")
    max_agent_steps: int = Field(default=5)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
