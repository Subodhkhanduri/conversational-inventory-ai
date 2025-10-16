from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Holds the application settings, loaded from environment variables.
    """
    groq_api_key: str = os.getenv("GROQ_API_KEY")

    class Config:
        # This allows pydantic to look for environment variables in a .env file
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a single instance of the settings to be imported elsewhere
settings = Settings()
