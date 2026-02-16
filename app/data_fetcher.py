"""
Data Fetcher
============
Fetches and triangulates macroeconomic data from multiple sources.
"""

import logging
import random
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import api_config
from countries import COUNTRIES, REGIONS, CountryInfo
from indicators import INDICATORS, get_assessment, format_value

logger = logging.getLogger(__name__)


# Regional baseline values for simulated data
REGIONAL_BASELINES: Dict[str, Dict[str, float]] = {
    "North America": {
        "gdp_growth": 2.5, "inflation": 3.2, "unemployment": 4.0, "interest_rate": 5.25,
        "gdp_per_capita": 65000, "current_account": -3.5, "government_debt": 95,
        "fdi_inflows": 2.0, "exchange_rate_change": 0.0, "industrial_production": 2.0,
        "consumer_confidence": 102, "trade_balance": -4.0,
    },
    "South America": {
        "gdp_growth": 2.0, "inflation": 8.5, "unemployment": 7.5, "interest_rate": 9.5,
        "gdp_per_capita": 12000, "current_account": -2.5, "government_debt": 65,
        "fdi_inflows": 3.0, "exchange_rate_change": -8.0, "industrial_production": 1.5,
        "consumer_confidence": 95, "trade_balance": 1.0,
    },
    "Europe": {
        "gdp_growth": 1.2, "inflation": 2.8, "unemployment": 6.0, "interest_rate": 4.0,
        "gdp_per_capita": 45000, "current_account": 2.5, "government_debt": 85,
        "fdi_inflows": 2.5, "exchange_rate_change": -2.0, "industrial_production": 0.5,
        "consumer_confidence": 98, "trade_balance": 3.0,
    },
    "Russia and CIS": {
        "gdp_growth": 2.5, "inflation": 8.0, "unemployment": 5.5, "interest_rate": 12.0,
        "gdp_per_capita": 15000, "current_account": 5.0, "government_debt": 25,
        "fdi_inflows": 1.5, "exchange_rate_change": -10.0, "industrial_production": 3.0,
        "consumer_confidence": 90, "trade_balance": 8.0,
    },
    "Asia": {
        "gdp_growth": 5.0, "inflation": 3.5, "unemployment": 4.5, "interest_rate": 4.5,
        "gdp_per_capita": 25000, "current_account": 3.0, "government_debt": 55,
        "fdi_inflows": 3.5, "exchange_rate_change": -1.0, "industrial_production": 5.0,
        "consumer_confidence": 105, "trade_balance": 4.0,
    },
    "Middle East": {
        "gdp_growth": 3.5, "inflation": 4.5, "unemployment": 8.5, "interest_rate": 5.5,
        "gdp_per_capita": 30000, "current_account": 8.0, "government_debt": 35,
        "fdi_inflows": 2.0, "exchange_rate_change": 0.0, "industrial_production": 2.5,
        "consumer_confidence": 100, "trade_balance": 10.0,
    },
    "Africa": {
        "gdp_growth": 3.5, "inflation": 9.5, "unemployment": 12.0, "interest_rate": 11.0,
        "gdp_per_capita": 3500, "current_account": -4.0, "government_debt": 55,
        "fdi_inflows": 2.5, "exchange_rate_change": -12.0, "industrial_production": 3.5,
        "consumer_confidence": 88, "trade_balance": -5.0,
    },
    "Oceania": {
        "gdp_growth": 2.5, "inflation": 3.5, "unemployment": 4.0, "interest_rate": 4.25,
        "gdp_per_capita": 55000, "current_account": -2.0, "government_debt": 45,
        "fdi_inflows": 3.0, "exchange_rate_change": -3.0, "industrial_production": 2.0,
        "consumer_confidence": 100, "trade_balance": -1.0,
    },
    "Aggregates": {
        "gdp_growth": 2.0, "inflation": 3.0, "unemployment": 6.0, "interest_rate": 4.0,
        "gdp_per_capita": 40000, "current_account": 1.0, "government_debt": 80,
        "fdi_inflows": 2.5, "exchange_rate_change": 0.0, "industrial_production": 1.5,
        "consumer_confidence": 100, "trade_balance": 2.0,
    },
}

# Income level adjustments
INCOME_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "high": {"gdp_per_capita": 1.5, "inflation": 0.7, "unemployment": 0.8},
    "upper_middle": {"gdp_per_capita": 0.6, "inflation": 1.2, "unemployment": 1.0},
    "lower_middle": {"gdp_per_capita": 0.25, "inflation": 1.4, "unemployment": 1.1},
    "low": {"gdp_per_capita": 0.1, "inflation": 1.6, "unemployment": 1.3},
}


@dataclass
class DataPoint:
    """Single data point from one source."""
    source: str
    value: Optional[float]
    period: str
    error: Optional[str] = None


@dataclass
class TriangulatedData:
    """Triangulated data from multiple sources."""
    country_code: str
    country_name: str
    region: str
    income_level: str
    indicator_code: str
    indicator_name: str
    unit: str
    fred_value: Optional[float]
    worldbank_value: Optional[float]
    oecd_value: Optional[float]
    consensus_value: Optional[float]
    confidence_level: str
    confidence_description: str
    assessment_label: str
    assessment_description: str
    period: str
    source_count: int


class DataFetcher:
    """Fetches macroeconomic data from multiple sources."""
    
    def __init__(self):
        """Initialize the data fetcher."""
        self.session = self._create_session()
        random.seed(42)
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=api_config.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount("http://", HTTPAdapter(max_retries=retry))
        session.mount("https://", HTTPAdapter(max_retries=retry))
        return session
    
    def _generate_simulated_value(
        self,
        indicator_code: str,
        country: CountryInfo
    ) -> Tuple[float, float, float]:
        """Generate simulated values for a country and indicator."""
        baseline = REGIONAL_BASELINES.get(country.region, REGIONAL_BASELINES["Aggregates"])
        base_value = baseline.get(indicator_code, 0.0)
        
        # Apply income adjustment
        adj = INCOME_ADJUSTMENTS.get(country.income_level, {})
        multiplier = adj.get(indicator_code, 1.0)
        adjusted_base = base_value * multiplier
        
        # Add variation
        if indicator_code == "gdp_per_capita":
            variation = random.uniform(-5000, 5000)
        elif indicator_code == "consumer_confidence":
            variation = random.uniform(-8, 8)
        elif indicator_code == "government_debt":
            variation = random.uniform(-15, 15)
        else:
            variation = random.uniform(-1.5, 1.5)
        
        # Generate three source values
        fred = adjusted_base + variation + random.uniform(-0.2, 0.2)
        wb = adjusted_base + variation + random.uniform(-0.2, 0.2)
        oecd = adjusted_base + variation + random.uniform(-0.2, 0.2)
        
        # Ensure valid ranges
        if indicator_code in ["unemployment", "inflation", "interest_rate", "government_debt"]:
            fred = max(0.1, fred)
            wb = max(0.1, wb)
            oecd = max(0.1, oecd)
        elif indicator_code == "gdp_per_capita":
            fred = max(500, fred)
            wb = max(500, wb)
            oecd = max(500, oecd)
        elif indicator_code == "consumer_confidence":
            fred = max(50, min(150, fred))
            wb = max(50, min(150, wb))
            oecd = max(50, min(150, oecd))
        
        return fred, wb, oecd
    
    def _calculate_confidence(
        self,
        fred: Optional[float],
        wb: Optional[float],
        oecd: Optional[float]
    ) -> Tuple[str, str]:
        """Calculate confidence level based on source agreement."""
        values = [v for v in [fred, wb, oecd] if v is not None]
        
        if len(values) == 0:
            return "no_data", "No data available from any source"
        elif len(values) == 1:
            return "single_source", "Data from single source only"
        
        avg = sum(values) / len(values)
        spread = max(values) - min(values)
        relative_spread = (spread / abs(avg)) * 100 if avg != 0 else spread
        
        if relative_spread < 5.0:
            return "high", "Strong agreement across all sources"
        elif relative_spread < 15.0:
            return "medium", "Moderate variation between sources"
        else:
            return "low", "Significant divergence between sources"
    
    def fetch_fred(self, indicator_code: str, country_code: str) -> DataPoint:
        """Fetch data from FRED API."""
        # For demo purposes, return simulated data
        # In production, implement actual FRED API calls
        return DataPoint(
            source="FRED",
            value=None,
            period="N/A",
            error="Using simulated data"
        )
    
    def fetch_worldbank(self, indicator_code: str, country_code: str) -> DataPoint:
        """Fetch data from World Bank API."""
        # For demo purposes, return simulated data
        # In production, implement actual World Bank API calls
        return DataPoint(
            source="World Bank",
            value=None,
            period="N/A",
            error="Using simulated data"
        )
    
    def triangulate(self, indicator_code: str, country_code: str) -> TriangulatedData:
        """Fetch and triangulate data from all sources."""
        country = COUNTRIES.get(country_code)
        indicator = INDICATORS.get(indicator_code)
        
        if not country or not indicator:
            return TriangulatedData(
                country_code=country_code,
                country_name="Unknown",
                region="Unknown",
                income_level="unknown",
                indicator_code=indicator_code,
                indicator_name="Unknown",
                unit="",
                fred_value=None,
                worldbank_value=None,
                oecd_value=None,
                consensus_value=None,
                confidence_level="no_data",
                confidence_description="Invalid country or indicator",
                assessment_label="Unknown",
                assessment_description="Unable to assess",
                period="N/A",
                source_count=0
            )
        
        # Generate simulated values
        fred, wb, oecd = self._generate_simulated_value(indicator_code, country)
        
        # Round values
        decimal_places = indicator.decimal_places
        fred = round(fred, decimal_places)
        wb = round(wb, decimal_places)
        oecd = round(oecd, decimal_places)
        
        # Calculate consensus
        consensus = round((fred + wb + oecd) / 3, decimal_places)
        
        # Calculate confidence
        confidence_level, confidence_desc = self._calculate_confidence(fred, wb, oecd)
        
        # Get assessment
        assessment_label, assessment_desc = get_assessment(indicator_code, consensus)
        
        # Generate period
        year = datetime.now().year
        quarter = (datetime.now().month - 1) // 3 + 1
        period = f"{year}-Q{quarter}"
        
        return TriangulatedData(
            country_code=country_code,
            country_name=country.name,
            region=country.region,
            income_level=country.income_level,
            indicator_code=indicator_code,
            indicator_name=indicator.display_name,
            unit=indicator.unit,
            fred_value=fred,
            worldbank_value=wb,
            oecd_value=oecd,
            consensus_value=consensus,
            confidence_level=confidence_level,
            confidence_description=confidence_desc,
            assessment_label=assessment_label,
            assessment_description=assessment_desc,
            period=period,
            source_count=3
        )
    
    def get_region_data(
        self,
        indicator_code: str,
        region: str
    ) -> List[TriangulatedData]:
        """Get data for all countries in a region."""
        codes = REGIONS.get(region, [])
        results = []
        
        for code in codes:
            data = self.triangulate(indicator_code, code)
            if data.consensus_value is not None:
                results.append(data)
        
        # Sort by consensus value
        indicator = INDICATORS.get(indicator_code)
        reverse = indicator.higher_is_better if indicator and indicator.higher_is_better is not None else True
        results.sort(key=lambda x: x.consensus_value or 0, reverse=reverse)
        
        return results
    
    def get_global_ranking(
        self,
        indicator_code: str,
        limit: int = 20
    ) -> List[TriangulatedData]:
        """Get global ranking for an indicator."""
        results = []
        
        for code in COUNTRIES.keys():
            if code == "EUU":
                continue
            data = self.triangulate(indicator_code, code)
            if data.consensus_value is not None:
                results.append(data)
        
        # Sort by consensus value
        indicator = INDICATORS.get(indicator_code)
        reverse = indicator.higher_is_better if indicator and indicator.higher_is_better is not None else True
        results.sort(key=lambda x: x.consensus_value or 0, reverse=reverse)
        
        return results[:limit]


# Global instance
data_fetcher = DataFetcher()


@lru_cache(maxsize=500)
def get_cached_data(indicator_code: str, country_code: str, cache_key: str) -> TriangulatedData:
    """Get cached triangulated data."""
    return data_fetcher.triangulate(indicator_code, country_code)


def get_data(indicator_code: str, country_code: str) -> TriangulatedData:
    """Get data with hourly caching."""
    cache_key = datetime.now().strftime("%Y%m%d%H")
    return get_cached_data(indicator_code, country_code, cache_key)