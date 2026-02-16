"""
Financial LLM Copilot - Data Pipeline
=====================================
Generates training data for 80+ countries with 12 macroeconomic indicators.

Indicators:
    1. GDP Growth Rate
    2. Inflation Rate
    3. Unemployment Rate
    4. Interest Rate
    5. GDP Per Capita
    6. Current Account Balance
    7. Government Debt
    8. FDI Inflows
    9. Exchange Rate Change
    10. Industrial Production
    11. Consumer Confidence
    12. Trade Balance

Coverage:
    - 80+ countries
    - 15 regions
    - Multiple data sources (FRED, World Bank, OECD)
"""

__version__ = "2.0.0"
__author__ = "Financial LLM Copilot"

from .config import PipelineConfig, config
from .countries import COUNTRIES, REGIONS, CountryInfo
from .indicators import INDICATORS, IndicatorConfig
from .data_generator import DataGenerator
from .training_data_builder import TrainingDataBuilder

__all__ = [
    "PipelineConfig",
    "config",
    "COUNTRIES",
    "REGIONS",
    "CountryInfo",
    "INDICATORS",
    "IndicatorConfig",
    "DataGenerator",
    "TrainingDataBuilder",
]