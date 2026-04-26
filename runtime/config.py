"""Configuration Management - Reusable across all projects"""

from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for all projects"""
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mistral")
    LLM_ENDPOINT: str = os.getenv("LLM_ENDPOINT", "http://localhost:11434/api/generate")
    LLM_REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("LLM_REQUEST_TIMEOUT_SECONDS", "1800"))
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY: Optional[str] = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY: Optional[str] = os.getenv("AWS_SECRET_KEY")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_DEBUG: bool = os.getenv("API_DEBUG", "false").lower() == "true"
    
    # Database Configuration
    DB_URL: str = os.getenv("DB_URL", "sqlite:///memory.db")
    
    # Frontend Configuration
    FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "localhost")
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "8501"))
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration"""
        config = {
            "provider": cls.LLM_PROVIDER,
            "model": cls.LLM_MODEL,
            "timeout_seconds": cls.LLM_REQUEST_TIMEOUT_SECONDS,
        }
        
        if cls.LLM_PROVIDER == "ollama":
            config["endpoint"] = cls.LLM_ENDPOINT
        elif cls.LLM_PROVIDER == "bedrock":
            config["region"] = cls.AWS_REGION
            if cls.AWS_ACCESS_KEY and cls.AWS_SECRET_KEY:
                config["credentials"] = {
                    "aws_access_key": cls.AWS_ACCESS_KEY,
                    "aws_secret_key": cls.AWS_SECRET_KEY
                }
        elif cls.LLM_PROVIDER == "openai":
            config["api_key"] = os.getenv("OPENAI_API_KEY")
        
        return config
    
    @classmethod
    def get_aws_config(cls) -> Dict[str, Any]:
        """Get AWS configuration"""
        config = {
            "region": cls.AWS_REGION
        }
        
        if cls.AWS_ACCESS_KEY and cls.AWS_SECRET_KEY:
            config["credentials"] = {
                "aws_access_key": cls.AWS_ACCESS_KEY,
                "aws_secret_key": cls.AWS_SECRET_KEY
            }
        
        return config
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration"""
        if cls.LLM_PROVIDER == "bedrock":
            if not cls.AWS_ACCESS_KEY or not cls.AWS_SECRET_KEY:
                raise ValueError("AWS credentials required for Bedrock")
        elif cls.LLM_PROVIDER == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OpenAI API key required")
