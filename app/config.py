"""
Application Configuration
=========================
Central configuration for the Streamlit application.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    # Try multiple .env locations (local dev + Docker/HF Spaces)
    for env_candidate in [
        Path(__file__).parent.parent / ".env",  # Local dev: project_root/.env
        Path(__file__).parent / ".env",          # Same dir as config.py
        Path("/app/.env"),                       # Docker container
    ]:
        if env_candidate.exists():
            load_dotenv(env_candidate)
            break
    load_dotenv()  # Also load from CWD as fallback
except ImportError:
    pass


@dataclass
class ModelConfig:
    """Configuration for the LLM model."""
    
    # HuggingFace Repository
    hf_repo_id: str = field(
        default_factory=lambda: os.environ.get(
            "HF_REPO_ID",
            "your-username/financial-copilot-80countries-12indicators-gguf"
        )
    )
    hf_filename: str = field(
        default_factory=lambda: os.environ.get(
            "HF_MODEL_FILENAME",
            "mistral-7b-instruct-v0.3.Q4_K_M.gguf"
        )
    )
    # Local paths
    local_model_dir: str = "models"
    local_model_path: str = "models/financial-copilot.gguf"
    
    # Model parameters
    n_ctx: int = field(
        default_factory=lambda: int(os.environ.get("MODEL_CONTEXT_LENGTH", "768"))
    )
    n_threads: int = field(
        default_factory=lambda: int(os.environ.get("MODEL_THREADS", "2"))
    )
    n_gpu_layers: int = field(
        default_factory=lambda: int(os.environ.get("MODEL_GPU_LAYERS", "0"))
    )
    
    # Generation parameters
    max_tokens: int = field(
        default_factory=lambda: int(os.environ.get("MODEL_MAX_TOKENS", "500"))
    )
    temperature: float = field(
        default_factory=lambda: float(os.environ.get("MODEL_TEMPERATURE", "0.7"))
    )
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1


@dataclass
class APIConfig:
    """Configuration for external APIs."""
    
    # FRED API
    fred_api_key: str = field(
        default_factory=lambda: os.environ.get("FRED_API_KEY", "")
    )
    fred_base_url: str = "https://api.stlouisfed.org/fred"
    
    # World Bank API
    worldbank_base_url: str = "https://api.worldbank.org/v2"
    
    # OECD API
    oecd_base_url: str = "https://sdmx.oecd.org/public/rest/data"
    
    # Request settings
    timeout: int = 30
    max_retries: int = 3


@dataclass
class AppConfig:
    """Configuration for the Streamlit application."""
    
    # App metadata
    app_title: str = "Financial LLM Copilot"
    app_icon: str = "logo.png"
    app_description: str = "AI-powered macroeconomic analysis for 80+ countries"
    app_version: str = "2.0.0"
    
    # UI settings
    max_chat_history: int = 50
    default_region: str = "Asia - South"
    default_countries_compare: List[str] = field(
        default_factory=lambda: ["USA", "CHN", "IND"]
    )
    
    # Feature flags
    enable_live_data: bool = True
    enable_charts: bool = True
    enable_comparisons: bool = True
    enable_rankings: bool = True
    
    # Cache settings
    cache_ttl: int = field(
        default_factory=lambda: int(os.environ.get("DATA_CACHE_TTL", "3600"))
    )


# Global configuration instances
model_config = ModelConfig()
api_config = APIConfig()
app_config = AppConfig()


def validate_config() -> Dict[str, any]:
    """Validate configuration and return status."""
    status = {
        "model_configured": False,
        "fred_api_configured": False,
        "warnings": [],
        "errors": []
    }
    
    # Check model configuration
    if "your-username" not in model_config.hf_repo_id:
        status["model_configured"] = True
    else:
        status["errors"].append("HF_REPO_ID not configured - update with your HuggingFace repo")
    
    # Check FRED API
    if api_config.fred_api_key:
        status["fred_api_configured"] = True
    else:
        status["warnings"].append("FRED_API_KEY not set - live FRED data unavailable")
    
    return status