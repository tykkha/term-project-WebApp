from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_HOST: str = "localhost"
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "Tinykitten73&"
    DATABASE_NAME: str = "gatorguides"
    
    class Config:
        env_file = ".env"

settings = Settings()