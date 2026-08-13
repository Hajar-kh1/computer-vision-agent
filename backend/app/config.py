"""Application settings (spec §28, §34).

TODO (Student 2 — Backend Engineer):
- Use pydantic-settings BaseSettings reading from env / .env.
- Fields (from .env.example):
      DATABASE_URL, MODEL_PATH, MODEL_VERSION, CORS_ORIGINS,
      MAX_UPLOAD_MB, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, DEBUG
- Parse CORS_ORIGINS (comma-separated) into a list.
- Provide a classmethod/property `cors_origins: list[str]`.
"""

# from pydantic_settings import BaseSettings
#
# class Settings(BaseSettings):
#     DATABASE_URL: str = "postgresql+psycopg://cvuser:cvpassword@localhost:5432/cvapp"
#     MODEL_PATH: str = "models/model.pt"
#     MODEL_VERSION: str = "1.0.0"
#     ...
#
#     model_config = SettingsConfigDict(env_file=".env", extra="ignore")
#
# settings = Settings()
