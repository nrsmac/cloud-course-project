from pydantic import (
    BaseModel,
    Field,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """Settings for Files API.

    Using pydantic-settings to load settings from environment variables.
    Pydantic BaseSettings Docs: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
    Fast API Settings Docs: https://fastapi.tiangolo.com/advanced/settings/
    """

    s3_bucket_name: str = Field(...)

    model_config = SettingsConfigDict(case_sensitive=False)
