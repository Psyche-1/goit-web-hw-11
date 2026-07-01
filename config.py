import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

class Settings:
    POSTGRES_USER: str = "my_api_user"
    POSTGRES_DB: str = "contacts_db"
    POSTGRES_HOST: str = "127.0.0.1"  
    POSTGRES_PORT: str = "5445" 

    @property
    def DATABASE_URL(self) -> str:
        # Убираем пароль из строки, так как база работает в режиме trust
        return f"postgresql://{self.POSTGRES_USER}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
print(f"--- ФИНАЛЬНОЕ ПОДКЛЮЧЕНИЕ: {settings.DATABASE_URL} ---")
