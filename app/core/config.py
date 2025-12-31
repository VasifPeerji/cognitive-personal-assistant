from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CognitivePersonalAssistant"
    ENV: str = "development"

    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    SECRET_KEY: str = "unsafe-default"

    class Config:
        env_file = ".env"


settings = Settings()
