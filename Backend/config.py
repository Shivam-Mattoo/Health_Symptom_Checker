import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the Backend directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Configuration class for application settings"""
    
    MONGO_URI = os.getenv("MONGO_URI", "")
    GEMINI_KEY = os.getenv("GEMINI_KEY", "")
    PINECONE_API = os.getenv("PINECONE_API", "")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "healthchecker")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = {
            "MONGO_URI": cls.MONGO_URI,
            "GEMINI_KEY": cls.GEMINI_KEY,
            "PINECONE_API": cls.PINECONE_API,
            "PINECONE_INDEX": cls.PINECONE_INDEX,
            "JWT_SECRET_KEY": cls.JWT_SECRET_KEY
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True

