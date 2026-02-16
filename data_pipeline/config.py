"""
Data Pipeline Configuration
===========================
Central configuration for the data pipeline.
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)
load_dotenv()


@dataclass
class PipelineConfig:
    """Configuration for the data pipeline."""
    
    # API Keys
    fred_api_key: str = field(
        default_factory=lambda: os.getenv("FRED_API_KEY", "")
    )
    
    # API Endpoints
    fred_base_url: str = "https://api.stlouisfed.org/fred"
    worldbank_base_url: str = "https://api.worldbank.org/v2"
    oecd_base_url: str = "https://sdmx.oecd.org/public/rest/data"
    
    # Request Settings
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Output Settings
    output_dir: str = field(
        default_factory=lambda: str(Path(__file__).parent / "output")
    )
    training_data_file: str = "training_data.jsonl"
    validation_data_file: str = "validation_data.jsonl"
    metadata_file: str = "metadata.json"
    
    # Data Generation Settings
    samples_per_country_indicator: int = 3
    include_comparisons: bool = True
    include_regional_analysis: bool = True
    include_rankings: bool = True
    include_multi_indicator: bool = True
    
    # Comparison Settings
    max_comparison_pairs: int = 50
    
    # Validation Split
    validation_split: float = 0.1
    
    # Random Seed
    seed: int = 42
    
    # Logging
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(self.output_dir, exist_ok=True)
    
    @property
    def training_data_path(self) -> Path:
        """Full path to training data file."""
        return Path(self.output_dir) / self.training_data_file
    
    @property
    def validation_data_path(self) -> Path:
        """Full path to validation data file."""
        return Path(self.output_dir) / self.validation_data_file
    
    @property
    def metadata_path(self) -> Path:
        """Full path to metadata file."""
        return Path(self.output_dir) / self.metadata_file
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of warnings."""
        warnings = []
        
        if not self.fred_api_key:
            warnings.append("FRED_API_KEY not set - live FRED data will be unavailable")
        
        if self.validation_split < 0 or self.validation_split > 0.5:
            warnings.append("validation_split should be between 0 and 0.5")
        
        return warnings


# Global configuration instance
config = PipelineConfig()