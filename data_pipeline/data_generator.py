"""
Data Generator
==============
Generates simulated macroeconomic data for training.
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .config import config
from .countries import COUNTRIES, REGIONS, CountryInfo
from .indicators import INDICATORS, IndicatorConfig, get_assessment, format_value


# Regional baseline values for all indicators
REGIONAL_BASELINES: Dict[str, Dict[str, float]] = {
    "North America": {
        "gdp_growth": 2.5,
        "inflation": 3.2,
        "unemployment": 4.0,
        "interest_rate": 5.25,
        "gdp_per_capita": 65000,
        "current_account": -3.5,
        "government_debt": 95,
        "fdi_inflows": 2.0,
        "exchange_rate_change": 0.0,
        "industrial_production": 2.0,
        "consumer_confidence": 102,
        "trade_balance": -4.0,
    },
    "South America": {
        "gdp_growth": 2.0,
        "inflation": 8.5,
        "unemployment": 7.5,
        "interest_rate": 9.5,
        "gdp_per_capita": 12000,
        "current_account": -2.5,
        "government_debt": 65,
        "fdi_inflows": 3.0,
        "exchange_rate_change": -8.0,
        "industrial_production": 1.5,
        "consumer_confidence": 95,
        "trade_balance": 1.0,
    },
    "Europe": {
        "gdp_growth": 1.2,
        "inflation": 2.8,
        "unemployment": 6.0,
        "interest_rate": 4.0,
        "gdp_per_capita": 45000,
        "current_account": 2.5,
        "government_debt": 85,
        "fdi_inflows": 2.5,
        "exchange_rate_change": -2.0,
        "industrial_production": 0.5,
        "consumer_confidence": 98,
        "trade_balance": 3.0,
    },
    "Russia and CIS": {
        "gdp_growth": 2.5,
        "inflation": 8.0,
        "unemployment": 5.5,
        "interest_rate": 12.0,
        "gdp_per_capita": 15000,
        "current_account": 5.0,
        "government_debt": 25,
        "fdi_inflows": 1.5,
        "exchange_rate_change": -10.0,
        "industrial_production": 3.0,
        "consumer_confidence": 90,
        "trade_balance": 8.0,
    },
    "Asia": {
        "gdp_growth": 5.0,
        "inflation": 3.5,
        "unemployment": 4.5,
        "interest_rate": 4.5,
        "gdp_per_capita": 25000,
        "current_account": 3.0,
        "government_debt": 55,
        "fdi_inflows": 3.5,
        "exchange_rate_change": -1.0,
        "industrial_production": 5.0,
        "consumer_confidence": 105,
        "trade_balance": 4.0,
    },
    "Middle East": {
        "gdp_growth": 3.5,
        "inflation": 4.5,
        "unemployment": 8.5,
        "interest_rate": 5.5,
        "gdp_per_capita": 30000,
        "current_account": 8.0,
        "government_debt": 35,
        "fdi_inflows": 2.0,
        "exchange_rate_change": 0.0,
        "industrial_production": 2.5,
        "consumer_confidence": 100,
        "trade_balance": 10.0,
    },
    "Africa": {
        "gdp_growth": 3.5,
        "inflation": 9.5,
        "unemployment": 12.0,
        "interest_rate": 11.0,
        "gdp_per_capita": 3500,
        "current_account": -4.0,
        "government_debt": 55,
        "fdi_inflows": 2.5,
        "exchange_rate_change": -12.0,
        "industrial_production": 3.5,
        "consumer_confidence": 88,
        "trade_balance": -5.0,
    },
    "Oceania": {
        "gdp_growth": 2.5,
        "inflation": 3.5,
        "unemployment": 4.0,
        "interest_rate": 4.25,
        "gdp_per_capita": 55000,
        "current_account": -2.0,
        "government_debt": 45,
        "fdi_inflows": 3.0,
        "exchange_rate_change": -3.0,
        "industrial_production": 2.0,
        "consumer_confidence": 100,
        "trade_balance": -1.0,
    },
    "Aggregates": {
        "gdp_growth": 2.0,
        "inflation": 3.0,
        "unemployment": 6.0,
        "interest_rate": 4.0,
        "gdp_per_capita": 40000,
        "current_account": 1.0,
        "government_debt": 80,
        "fdi_inflows": 2.5,
        "exchange_rate_change": 0.0,
        "industrial_production": 1.5,
        "consumer_confidence": 100,
        "trade_balance": 2.0,
    },
}

# Income level multipliers
INCOME_MULTIPLIERS: Dict[str, Dict[str, float]] = {
    "high": {
        "gdp_per_capita": 1.5,
        "inflation": 0.7,
        "unemployment": 0.8,
        "government_debt": 1.2,
        "fdi_inflows": 0.8,
        "consumer_confidence": 1.05,
    },
    "upper_middle": {
        "gdp_per_capita": 0.6,
        "inflation": 1.2,
        "unemployment": 1.0,
        "government_debt": 0.9,
        "fdi_inflows": 1.2,
        "consumer_confidence": 1.0,
    },
    "lower_middle": {
        "gdp_per_capita": 0.25,
        "inflation": 1.4,
        "unemployment": 1.1,
        "government_debt": 0.7,
        "fdi_inflows": 1.3,
        "consumer_confidence": 0.95,
    },
    "low": {
        "gdp_per_capita": 0.1,
        "inflation": 1.6,
        "unemployment": 1.3,
        "government_debt": 0.5,
        "fdi_inflows": 1.5,
        "consumer_confidence": 0.9,
    },
}


@dataclass
class MacroeconomicDataPoint:
    """Container for a single macroeconomic data point."""
    country_code: str
    country_name: str
    region: str
    sub_region: str
    income_level: str
    indicator_code: str
    indicator_name: str
    unit: str
    fred_value: float
    worldbank_value: float
    oecd_value: float
    consensus_value: float
    period: str
    assessment_label: str
    assessment_description: str
    confidence_level: str
    confidence_description: str


class DataGenerator:
    """Generates simulated macroeconomic data."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the data generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed or config.seed
        random.seed(self.seed)
    
    def _get_regional_baseline(self, region: str) -> Dict[str, float]:
        """Get baseline values for a region."""
        return REGIONAL_BASELINES.get(region, REGIONAL_BASELINES["Aggregates"])
    
    def _apply_income_adjustment(
        self, 
        base_value: float, 
        indicator_code: str, 
        income_level: str
    ) -> float:
        """Apply income level adjustment to a value."""
        multipliers = INCOME_MULTIPLIERS.get(income_level, {})
        multiplier = multipliers.get(indicator_code, 1.0)
        return base_value * multiplier
    
    def _add_variation(self, indicator_code: str) -> float:
        """Add random variation based on indicator type."""
        if indicator_code == "gdp_per_capita":
            return random.uniform(-5000, 5000)
        elif indicator_code == "consumer_confidence":
            return random.uniform(-8, 8)
        elif indicator_code == "government_debt":
            return random.uniform(-15, 15)
        else:
            return random.uniform(-1.5, 1.5)
    
    def _ensure_valid_range(self, value: float, indicator_code: str) -> float:
        """Ensure value is within valid range for indicator."""
        indicator = INDICATORS.get(indicator_code)
        if not indicator:
            return value
        
        min_val, max_val = indicator.value_range
        return max(min_val, min(max_val, value))
    
    def _calculate_confidence(
        self, 
        fred: float, 
        worldbank: float, 
        oecd: float
    ) -> Tuple[str, str]:
        """Calculate confidence level based on source agreement."""
        values = [fred, worldbank, oecd]
        avg = sum(values) / 3
        spread = max(values) - min(values)
        
        if avg == 0:
            relative_spread = spread
        else:
            relative_spread = (spread / abs(avg)) * 100
        
        if relative_spread < 3.0:
            return "High", "Strong agreement across all data sources"
        elif relative_spread < 8.0:
            return "Medium-High", "Sources agree within acceptable variance"
        elif relative_spread < 15.0:
            return "Medium", "Moderate variation between sources"
        else:
            return "Low", "Significant divergence requires verification"
    
    def generate_data_point(
        self, 
        country_code: str, 
        indicator_code: str
    ) -> Optional[MacroeconomicDataPoint]:
        """
        Generate a single data point for a country and indicator.
        
        Args:
            country_code: ISO country code
            indicator_code: Indicator code
            
        Returns:
            MacroeconomicDataPoint or None if invalid inputs
        """
        if country_code not in COUNTRIES:
            return None
        if indicator_code not in INDICATORS:
            return None
        
        country = COUNTRIES[country_code]
        indicator = INDICATORS[indicator_code]
        baseline = self._get_regional_baseline(country.region)
        
        # Get base value and apply adjustments
        base_value = baseline.get(indicator_code, 0.0)
        adjusted_value = self._apply_income_adjustment(
            base_value, indicator_code, country.income_level
        )
        
        # Add variation
        variation = self._add_variation(indicator_code)
        
        # Generate source values with small differences
        fred_value = self._ensure_valid_range(
            adjusted_value + variation + random.uniform(-0.15, 0.15),
            indicator_code
        )
        worldbank_value = self._ensure_valid_range(
            adjusted_value + variation + random.uniform(-0.15, 0.15),
            indicator_code
        )
        oecd_value = self._ensure_valid_range(
            adjusted_value + variation + random.uniform(-0.15, 0.15),
            indicator_code
        )
        
        # Calculate consensus
        consensus_value = round((fred_value + worldbank_value + oecd_value) / 3, 
                                indicator.decimal_places)
        
        # Get assessment
        assessment_label, assessment_description = get_assessment(
            indicator_code, consensus_value
        )
        
        # Get confidence
        confidence_level, confidence_description = self._calculate_confidence(
            fred_value, worldbank_value, oecd_value
        )
        
        # Generate period
        year = 2024
        quarter = random.randint(1, 4)
        period = f"{year}-Q{quarter}"
        
        return MacroeconomicDataPoint(
            country_code=country_code,
            country_name=country.name,
            region=country.region,
            sub_region=country.sub_region,
            income_level=country.income_level,
            indicator_code=indicator_code,
            indicator_name=indicator.display_name,
            unit=indicator.unit,
            fred_value=round(fred_value, indicator.decimal_places),
            worldbank_value=round(worldbank_value, indicator.decimal_places),
            oecd_value=round(oecd_value, indicator.decimal_places),
            consensus_value=consensus_value,
            period=period,
            assessment_label=assessment_label,
            assessment_description=assessment_description,
            confidence_level=confidence_level,
            confidence_description=confidence_description,
        )
    
    def generate_country_data(
        self, 
        country_code: str,
        indicators: Optional[List[str]] = None
    ) -> List[MacroeconomicDataPoint]:
        """
        Generate data for all indicators for a country.
        
        Args:
            country_code: ISO country code
            indicators: List of indicator codes (default: all)
            
        Returns:
            List of MacroeconomicDataPoint objects
        """
        if indicators is None:
            indicators = list(INDICATORS.keys())
        
        data_points = []
        for indicator_code in indicators:
            data_point = self.generate_data_point(country_code, indicator_code)
            if data_point:
                data_points.append(data_point)
        
        return data_points
    
    def generate_region_data(
        self, 
        region: str,
        indicator_code: str
    ) -> List[MacroeconomicDataPoint]:
        """
        Generate data for all countries in a region for one indicator.
        
        Args:
            region: Region name
            indicator_code: Indicator code
            
        Returns:
            List of MacroeconomicDataPoint objects
        """
        country_codes = REGIONS.get(region, [])
        data_points = []
        
        for country_code in country_codes:
            data_point = self.generate_data_point(country_code, indicator_code)
            if data_point:
                data_points.append(data_point)
        
        return data_points
    
    def generate_global_data(
        self, 
        indicator_code: str
    ) -> List[MacroeconomicDataPoint]:
        """
        Generate data for all countries for one indicator.
        
        Args:
            indicator_code: Indicator code
            
        Returns:
            List of MacroeconomicDataPoint objects sorted by value
        """
        data_points = []
        
        for country_code in COUNTRIES.keys():
            if country_code == "EUU":
                continue
            data_point = self.generate_data_point(country_code, indicator_code)
            if data_point:
                data_points.append(data_point)
        
        # Sort by consensus value
        indicator = INDICATORS.get(indicator_code)
        reverse = indicator.higher_is_better if indicator else True
        data_points.sort(key=lambda x: x.consensus_value, reverse=reverse)
        
        return data_points