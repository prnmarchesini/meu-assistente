"""Carrega as variaveis de ambiente do .env (pydantic-settings)."""
from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    # ── Supabase (Auth / Storage / API) ──
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_key: str | None = None

    # ── Conexoes Postgres ──
    # transaction pooler = 6543 ; session pooler = 5432.
    supabase_transaction_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_TRANSACTION_URL", "DATABASE_URL"),
    )
    supabase_pooler_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_POOLER_URL", "DIRECT_URL"),
    )

    # ── IA ──
    openai_api_key: str | None = None
    deepseek_api_key: str | None = None

    # ── Telegram ──
    telegram_bot_token: str | None = None
    telegram_webhook_secret: str | None = None
    telegram_bot_username: str | None = None

    # ── Infra ──
    railway_token: str | None = Field(
        default=None, validation_alias=AliasChoices("RAILWAY_TOKEN", "token_railway")
    )
    port: int = 8000

    @property
    def database_url(self) -> str | None:
        """URL de conexao do backend.

        Prefere o session pooler (5432), que conecta de forma estavel; cai para o
        transaction pooler (6543) se for o unico disponivel.
        """
        return self.supabase_pooler_url or self.supabase_transaction_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
