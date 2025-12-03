from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Node Microservice
    node_service_url: str = "http://localhost:5000"
    
    # FastAPI
    api_port: int = 8000
    debug: bool = True
    
    # AI Provider (optional for now)
    openai_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()