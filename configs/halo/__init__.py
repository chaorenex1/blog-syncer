from pydantic import Field
from pydantic_settings import BaseSettings


class HaloConfig(BaseSettings):

    HALO_BASE_URL: str = Field(default="http://localhost:8080", description="Base URL for the Halo service")
    HALO_API_KEY: str = Field(default="", description="API key for authenticating with the Halo service")
    HALO_TIMEOUT: int = Field(default=30, description="Timeout in seconds for Halo service requests")