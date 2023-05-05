from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    database_url: str = "sqlite:///backend/app.db"
    secret_key: str = "b89337b4d4383e4e33175824239f82f6961282323af21862caaa94a80b0ca8a7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1
    allowed_cors_origins: set[AnyUrl] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    # allowed_cors_origins = ["*"]


settings = Settings()
