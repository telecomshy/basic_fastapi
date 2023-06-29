from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    database_url: str = "sqlite:///app.db"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    allowed_cors_origins: set[AnyUrl] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    base_url: str = "/api/v1"
    test_username: str
    test_password: str

    class Config:
        env_file = "backend/.env"


settings = Settings()
