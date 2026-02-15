"""
API Data Fetcher
================
Fetches real macroeconomic data from FRED, World Bank, and OECD APIs.
This module is used for production data fetching (not for training data generation).
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import config
from .countries import COUNTRIES, CountryInfo
from .indicators import INDICATORS, IndicatorConfig

logger = logging.getLogger(__name__)


@dataclass
class APIDataPoint:
    """Container for data from a single API source."""
    source: str
    value: Optional[float]
    period: str
    retrieved_at: str
    error: Optional[str] = None


@dataclass
class TriangulatedData:
    """Container for triangulated data from multiple sources."""
    country_code: str
    country_name: str
    region: str
    indicator_code: str
    indicator_name: str
    unit: str
    fred_value: Optional[float]
    worldbank_value: Optional[float]
    oecd_value: Optional[float]
    consensus_value: Optional[float]
    confidence_level: str
    period: str
    source_count: int


class APIFetcher:
    """Fetches macroeconomic data from external APIs."""
    
    def __init__(self):
        """Initialize the API fetcher."""
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=config.max_retries,
            backoff_factor=config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(
        self, 
        url: str, 
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make an HTTP GET request with error handling."""
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=config.request_timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def fetch_fred(
        self, 
        indicator_code: str, 
        country_code: str
    ) -> APIDataPoint:
        """
        Fetch data from FRED API.
        
        Args:
            indicator_code: The indicator code
            country_code: ISO country code
            
        Returns:
            APIDataPoint with FRED data
        """
        if not config.fred_api_key:
            return APIDataPoint(
                source="FRED",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error="FRED API key not configured"
            )
        
        indicator = INDICATORS.get(indicator_code)
        country = COUNTRIES.get(country_code)
        
        if not indicator or not country:
            return APIDataPoint(
                source="FRED",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error="Invalid indicator or country code"
            )
        
        # Build series ID
        if not indicator.fred_series_template:
            return APIDataPoint(
                source="FRED",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error=f"No FRED series available for {indicator_code}"
            )
        
        fred_country = country.fred_code or country_code
        series_id = indicator.fred_series_template.format(country=fred_country)
        
        params = {
            "series_id": series_id,
            "api_key": config.fred_api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 10
        }
        
        url = f"{config.fred_base_url}/series/observations"
        data = self._make_request(url, params)
        
        if not data:
            return APIDataPoint(
                source="FRED",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error="Failed to fetch data from FRED"
            )
        
        # Extract latest valid observation
        observations = data.get("observations", [])
        for obs in observations:
            value_str = obs.get("value", ".")
            if value_str and value_str != ".":
                try:
                    value = float(value_str)
                    return APIDataPoint(
                        source="FRED",
                        value=value,
                        period=obs.get("date", "N/A"),
                        retrieved_at=datetime.now().isoformat()
                    )
                except ValueError:
                    continue
        
        return APIDataPoint(
            source="FRED",
            value=None,
            period="N/A",
            retrieved_at=datetime.now().isoformat(),
            error="No valid observations found"
        )
    
    def fetch_worldbank(
        self, 
        indicator_code: str, 
        country_code: str
    ) -> APIDataPoint:
        """
        Fetch data from World Bank API.
        
        Args:
            indicator_code: The indicator code
            country_code: ISO country code
            
        Returns:
            APIDataPoint with World Bank data
        """
        indicator = INDICATORS.get(indicator_code)
        country = COUNTRIES.get(country_code)
        
        if not indicator or not country:
            return APIDataPoint(
                source="World Bank",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error="Invalid indicator or country code"
            )
        
        if not indicator.worldbank_indicator:
            return APIDataPoint(
                source="World Bank",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error=f"No World Bank indicator available for {indicator_code}"
            )
        
        wb_country = country.worldbank_code or country_code
        wb_indicator = indicator.worldbank_indicator
        
        current_year = datetime.now().year
        params = {
            "format": "json",
            "per_page": 10,
            "date": f"{current_year - 5}:{current_year}"
        }
        
        url = f"{config.worldbank_base_url}/country/{wb_country}/indicator/{wb_indicator}"
        data = self._make_request(url, params)
        
        if not data or not isinstance(data, list) or len(data) < 2:
            return APIDataPoint(
                source="World Bank",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error="Failed to fetch data from World Bank"
            )
        
        # Extract latest valid observation
        observations = data[1] if data[1] else []
        for obs in observations:
            value = obs.get("value")
            if value is not None:
                try:
                    return APIDataPoint(
                        source="World Bank",
                        value=float(value),
                        period=str(obs.get("date", "N/A")),
                        retrieved_at=datetime.now().isoformat()
                    )
                except (ValueError, TypeError):
                    continue
        
        return APIDataPoint(
            source="World Bank",
            value=None,
            period="N/A",
            retrieved_at=datetime.now().isoformat(),
            error="No valid observations found"
        )
    
    def fetch_oecd(
        self, 
        indicator_code: str, 
        country_code: str
    ) -> APIDataPoint:
        """
        Fetch data from OECD API.
        
        Args:
            indicator_code: The indicator code
            country_code: ISO country code
            
        Returns:
            APIDataPoint with OECD data
        """
        indicator = INDICATORS.get(indicator_code)
        country = COUNTRIES.get(country_code)
        
        if not indicator or not country:
            return APIDataPoint(
                source="OECD",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error="Invalid indicator or country code"
            )
        
        if not country.is_oecd_member:
            return APIDataPoint(
                source="OECD",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error=f"{country.name} is not an OECD member"
            )
        
        if not indicator.oecd_dataset:
            return APIDataPoint(
                source="OECD",
                value=None,
                period="N/A",
                retrieved_at=datetime.now().isoformat(),
                error=f"No OECD dataset available for {indicator_code}"
            )
        
        # OECD API implementation would go here
        # For now, return a placeholder
        return APIDataPoint(
            source="OECD",
            value=None,
            period="N/A",
            retrieved_at=datetime.now().isoformat(),
            error="OECD API not fully implemented"
        )
    
    def triangulate(
        self, 
        indicator_code: str, 
        country_code: str
    ) -> TriangulatedData:
        """
        Fetch and triangulate data from all sources.
        
        Args:
            indicator_code: The indicator code
            country_code: ISO country code
            
        Returns:
            TriangulatedData with consensus value
        """
        country = COUNTRIES.get(country_code)
        indicator = INDICATORS.get(indicator_code)
        
        if not country or not indicator:
            return TriangulatedData(
                country_code=country_code,
                country_name="Unknown",
                region="Unknown",
                indicator_code=indicator_code,
                indicator_name="Unknown",
                unit="",
                fred_value=None,
                worldbank_value=None,
                oecd_value=None,
                consensus_value=None,
                confidence_level="no_data",
                period="N/A",
                source_count=0
            )
        
        # Fetch from all sources
        fred_data = self.fetch_fred(indicator_code, country_code)
        worldbank_data = self.fetch_worldbank(indicator_code, country_code)
        oecd_data = self.fetch_oecd(indicator_code, country_code)
        
        # Collect valid values
        values = []
        if fred_data.value is not None:
            values.append(fred_data.value)
        if worldbank_data.value is not None:
            values.append(worldbank_data.value)
        if oecd_data.value is not None:
            values.append(oecd_data.value)
        
        # Calculate consensus and confidence
        if len(values) == 0:
            consensus = None
            confidence = "no_data"
        elif len(values) == 1:
            consensus = values[0]
            confidence = "single_source"
        else:
            consensus = sum(values) / len(values)
            spread = max(values) - min(values)
            avg = sum(values) / len(values)
            relative_spread = (spread / abs(avg)) * 100 if avg != 0 else spread
            
            if relative_spread < 5.0:
                confidence = "high"
            elif relative_spread < 15.0:
                confidence = "medium"
            else:
                confidence = "low"
        
        # Determine period
        periods = [fred_data.period, worldbank_data.period, oecd_data.period]
        period = next((p for p in periods if p != "N/A"), "N/A")
        
        return TriangulatedData(
            country_code=country_code,
            country_name=country.name,
            region=country.region,
            indicator_code=indicator_code,
            indicator_name=indicator.display_name,
            unit=indicator.unit,
            fred_value=fred_data.value,
            worldbank_value=worldbank_data.value,
            oecd_value=oecd_data.value,
            consensus_value=round(consensus, indicator.decimal_places) if consensus else None,
            confidence_level=confidence,
            period=period,
            source_count=len(values)
        )
    
    def fetch_region_data(
        self, 
        indicator_code: str, 
        region: str
    ) -> List[TriangulatedData]:
        """
        Fetch data for all countries in a region.
        
        Args:
            indicator_code: The indicator code
            region: Region name
            
        Returns:
            List of TriangulatedData for the region
        """
        from .countries import REGIONS
        
        country_codes = REGIONS.get(region, [])
        results = []
        
        for country_code in country_codes:
            data = self.triangulate(indicator_code, country_code)
            if data.consensus_value is not None:
                results.append(data)
            time.sleep(0.1)  # Rate limiting
        
        # Sort by consensus value
        indicator = INDICATORS.get(indicator_code)
        reverse = indicator.higher_is_better if indicator else True
        results.sort(key=lambda x: x.consensus_value or 0, reverse=reverse)
        
        return results
    
    def fetch_global_ranking(
        self, 
        indicator_code: str, 
        limit: int = 20
    ) -> List[TriangulatedData]:
        """
        Fetch global ranking for an indicator.
        
        Args:
            indicator_code: The indicator code
            limit: Maximum number of results
            
        Returns:
            List of TriangulatedData sorted by value
        """
        results = []
        
        for country_code in COUNTRIES.keys():
            if country_code == "EUU":
                continue
            
            data = self.triangulate(indicator_code, country_code)
            if data.consensus_value is not None:
                results.append(data)
            time.sleep(0.1)  # Rate limiting
        
        # Sort by consensus value
        indicator = INDICATORS.get(indicator_code)
        reverse = indicator.higher_is_better if indicator else True
        results.sort(key=lambda x: x.consensus_value or 0, reverse=reverse)
        
        return results[:limit]


# Global instance
api_fetcher = APIFetcher()