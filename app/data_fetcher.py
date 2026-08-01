"""
Data Fetcher
============
Fetches and triangulates macroeconomic data from multiple sources.

Two modes are supported per lookup:

* ``live``     - values come from upstream APIs (FRED, World Bank). Only real
                 observations feed the consensus.
* ``modelled`` - values come from a deterministic regional baseline model, used
                 when live sources return nothing (no coverage, no API key,
                 upstream failure, or live mode switched off).

The two are never averaged together: mixing a real observation with a synthetic
one would produce a number that means nothing. Every result carries a
``source_mode`` so the UI and the prompt context can say which it is.
"""

import logging
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import api_config
from countries import COUNTRIES, REGIONS, CountryInfo, get_fred_code, is_oecd_member
from indicators import INDICATORS, get_assessment

logger = logging.getLogger(__name__)


# Regional baseline values for the modelled fallback
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

# Income level adjustments applied to the modelled baselines
INCOME_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "high": {"gdp_per_capita": 1.5, "inflation": 0.7, "unemployment": 0.8},
    "upper_middle": {"gdp_per_capita": 0.6, "inflation": 1.2, "unemployment": 1.0},
    "lower_middle": {"gdp_per_capita": 0.25, "inflation": 1.4, "unemployment": 1.1},
    "low": {"gdp_per_capita": 0.1, "inflation": 1.6, "unemployment": 1.3},
}

# Source mode constants
MODE_LIVE = "live"
MODE_MODELLED = "modelled"

# Seed for the modelled fallback. Combined with the country and indicator so a
# given pair always yields the same value, independent of call order or thread.
_MODEL_SEED = 42


@dataclass
class DataPoint:
    """Single observation from one source."""
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
    # Whether consensus_value came from upstream APIs or the baseline model.
    source_mode: str = MODE_MODELLED
    # Human-readable provenance, e.g. "World Bank (2025)".
    source_note: str = ""

    @property
    def is_live(self) -> bool:
        """True when the consensus is built from real upstream observations."""
        return self.source_mode == MODE_LIVE


class DataFetcher:
    """Fetches macroeconomic data from live APIs with a modelled fallback."""

    def __init__(self):
        """Initialize the data fetcher."""
        # requests.Session is not designed for concurrent use, and bulk sweeps
        # run on a thread pool, so each thread gets its own session.
        self._local = threading.local()

    # -------------------------------------------------------------------------
    # HTTP plumbing
    # -------------------------------------------------------------------------
    @property
    def session(self) -> requests.Session:
        """Return this thread's session, creating it on first use."""
        session = getattr(self._local, "session", None)
        if session is None:
            session = self._create_session()
            self._local.session = session
        return session

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=api_config.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry, pool_maxsize=api_config.bulk_max_workers)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _get_json(
        self,
        url: str,
        params: Optional[Dict] = None,
        timeout: Optional[int] = None
    ):
        """GET a URL and return parsed JSON, or None on any failure."""
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=timeout or api_config.live_timeout,
            )
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.debug(f"Request failed for {url}: {e}")
            return None

    # -------------------------------------------------------------------------
    # FRED
    # -------------------------------------------------------------------------
    def fetch_fred(
        self,
        indicator_code: str,
        country_code: str,
        timeout: Optional[int] = None
    ) -> DataPoint:
        """
        Fetch the latest observation for an indicator from FRED.

        FRED offers no batch endpoint, so this is one request per series and is
        only used for single-country lookups, not bulk sweeps.
        """
        if not api_config.fred_api_key:
            return DataPoint("FRED", None, "N/A", error="FRED API key not configured")

        indicator = INDICATORS.get(indicator_code)
        if not indicator or not indicator.fred_series_template:
            return DataPoint("FRED", None, "N/A", error="No FRED series mapped")

        fred_country = get_fred_code(country_code)
        if not fred_country:
            return DataPoint("FRED", None, "N/A", error="No FRED country code")

        series_id = indicator.fred_series_template.format(country=fred_country)
        payload = self._get_json(
            f"{api_config.fred_base_url}/series/observations",
            params={
                "series_id": series_id,
                "api_key": api_config.fred_api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 24,
            },
            timeout=timeout,
        )

        # A missing or discontinued series returns an error payload, not a 404.
        if not payload or "observations" not in payload:
            return DataPoint("FRED", None, "N/A", error=f"Series unavailable: {series_id}")

        for obs in payload["observations"]:
            value = _parse_float(obs.get("value"))
            if value is None:
                continue
            if not _within_range(value, indicator):
                continue
            return DataPoint("FRED", value, obs.get("date", "N/A"))

        return DataPoint("FRED", None, "N/A", error="No valid observations")

    # -------------------------------------------------------------------------
    # World Bank
    # -------------------------------------------------------------------------
    def fetch_worldbank_batch(
        self,
        indicator_code: str,
        country_codes: Iterable[str],
        timeout: Optional[int] = None
    ) -> Dict[str, DataPoint]:
        """
        Fetch an indicator for many countries using batched requests.

        The World Bank API accepts semicolon-separated ISO-3 codes, so a
        100-country sweep costs a handful of calls instead of a hundred.

        Returns:
            Mapping of country code to DataPoint. Countries with no usable
            observation are present with a value of None.
        """
        codes = [c for c in country_codes]
        indicator = INDICATORS.get(indicator_code)
        results: Dict[str, DataPoint] = {
            c: DataPoint("World Bank", None, "N/A", error="Not fetched") for c in codes
        }

        if not indicator or not indicator.worldbank_indicator:
            for c in codes:
                results[c] = DataPoint(
                    "World Bank", None, "N/A", error="No World Bank indicator mapped"
                )
            return results

        current_year = datetime.now().year
        date_range = f"{current_year - api_config.lookback_years}:{current_year}"
        size = max(1, api_config.worldbank_batch_size)
        chunks = [codes[i:i + size] for i in range(0, len(codes), size)]

        def fetch_chunk(chunk: List[str]) -> Dict[str, List[Tuple[str, float]]]:
            url = (
                f"{api_config.worldbank_base_url}/country/{';'.join(chunk)}"
                f"/indicator/{indicator.worldbank_indicator}"
            )
            payload = self._get_json(
                url,
                params={
                    "format": "json",
                    # Enough rows to cover every country/year in the chunk.
                    "per_page": len(chunk) * (api_config.lookback_years + 2),
                    "date": date_range,
                },
                timeout=timeout,
            )
            observations: Dict[str, List[Tuple[str, float]]] = {}
            # Shape is [paging_metadata, [observations]].
            if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
                return observations
            for obs in payload[1]:
                code = obs.get("countryiso3code") or ""
                value = _parse_float(obs.get("value"))
                if not code or value is None:
                    continue
                observations.setdefault(code, []).append((str(obs.get("date", "")), value))
            return observations

        merged: Dict[str, List[Tuple[str, float]]] = {}
        if len(chunks) == 1:
            merged.update(fetch_chunk(chunks[0]))
        else:
            workers = min(api_config.bulk_max_workers, len(chunks))
            with ThreadPoolExecutor(max_workers=workers) as pool:
                for chunk_result in pool.map(fetch_chunk, chunks):
                    merged.update(chunk_result)

        for code in codes:
            series = merged.get(code, [])
            if not series:
                results[code] = DataPoint(
                    "World Bank", None, "N/A", error="No observations in range"
                )
                continue
            # Newest first.
            series.sort(key=lambda item: item[0], reverse=True)
            results[code] = _worldbank_point(series, indicator)

        return results

    def fetch_worldbank(
        self,
        indicator_code: str,
        country_code: str,
        timeout: Optional[int] = None
    ) -> DataPoint:
        """Fetch a single country's latest World Bank observation."""
        batch = self.fetch_worldbank_batch(indicator_code, [country_code], timeout=timeout)
        return batch.get(
            country_code,
            DataPoint("World Bank", None, "N/A", error="No result"),
        )

    # -------------------------------------------------------------------------
    # OECD
    # -------------------------------------------------------------------------
    def fetch_oecd(self, indicator_code: str, country_code: str) -> DataPoint:
        """
        OECD SDMX client placeholder.

        Dataset IDs are mapped on each indicator and OECD membership is tracked
        in ``countries.OECD_MEMBERS``, but no request is made yet, so this
        always reports no data rather than inventing one.
        """
        indicator = INDICATORS.get(indicator_code)
        if not indicator or not indicator.oecd_dataset:
            return DataPoint("OECD", None, "N/A", error="No OECD dataset mapped")
        if not is_oecd_member(country_code):
            return DataPoint("OECD", None, "N/A", error="Not an OECD member")
        return DataPoint("OECD", None, "N/A", error="OECD client not implemented")

    # -------------------------------------------------------------------------
    # Modelled fallback
    # -------------------------------------------------------------------------
    def _modelled_values(
        self,
        indicator_code: str,
        country: CountryInfo
    ) -> Tuple[float, float, float]:
        """
        Generate the three modelled source values for a country and indicator.

        Seeded per country/indicator pair, so the same inputs always give the
        same output regardless of call order or which thread runs it. The
        previous implementation drew from the shared global RNG, which made
        results depend on request sequence and broke under the thread pool.
        """
        rng = random.Random(f"{_MODEL_SEED}:{country.code}:{indicator_code}")

        baseline = REGIONAL_BASELINES.get(country.region, REGIONAL_BASELINES["Aggregates"])
        base_value = baseline.get(indicator_code, 0.0)

        adj = INCOME_ADJUSTMENTS.get(country.income_level, {})
        adjusted_base = base_value * adj.get(indicator_code, 1.0)

        if indicator_code == "gdp_per_capita":
            variation = rng.uniform(-5000, 5000)
        elif indicator_code == "consumer_confidence":
            variation = rng.uniform(-8, 8)
        elif indicator_code == "government_debt":
            variation = rng.uniform(-15, 15)
        else:
            variation = rng.uniform(-1.5, 1.5)

        values = [
            adjusted_base + variation + rng.uniform(-0.2, 0.2) for _ in range(3)
        ]

        if indicator_code in ("unemployment", "inflation", "interest_rate", "government_debt"):
            values = [max(0.1, v) for v in values]
        elif indicator_code == "gdp_per_capita":
            values = [max(500, v) for v in values]
        elif indicator_code == "consumer_confidence":
            values = [max(50, min(150, v)) for v in values]

        return values[0], values[1], values[2]

    # -------------------------------------------------------------------------
    # Confidence
    # -------------------------------------------------------------------------
    def _calculate_confidence(self, values: List[float]) -> Tuple[str, str]:
        """Grade confidence from the spread across available sources."""
        if not values:
            return "no_data", "No data available from any source"
        if len(values) == 1:
            return "single_source", "Data from a single source only"

        avg = sum(values) / len(values)
        spread = max(values) - min(values)
        relative_spread = (spread / abs(avg)) * 100 if avg != 0 else spread

        if relative_spread < 5.0:
            return "high", "Strong agreement across all sources"
        if relative_spread < 15.0:
            return "medium", "Moderate variation between sources"
        return "low", "Significant divergence between sources"

    # -------------------------------------------------------------------------
    # Triangulation
    # -------------------------------------------------------------------------
    def triangulate(
        self,
        indicator_code: str,
        country_code: str,
        live: Optional[bool] = None,
        timeout: Optional[int] = None,
        worldbank_point: Optional[DataPoint] = None,
        include_fred: bool = True,
    ) -> TriangulatedData:
        """
        Fetch and triangulate an indicator for one country.

        Args:
            indicator_code: Indicator to fetch.
            country_code: ISO-3 country code.
            live: Force live or modelled mode. Defaults to the app setting.
            timeout: Per-request timeout override.
            worldbank_point: Pre-fetched World Bank observation, supplied by
                bulk sweeps so the batched result is not re-requested.
            include_fred: Set False to skip FRED. Bulk sweeps do this because
                FRED has no batch endpoint and one request per country would
                dominate the response time.

        Returns:
            TriangulatedData with a consensus value and its provenance.
        """
        country = COUNTRIES.get(country_code)
        indicator = INDICATORS.get(indicator_code)

        if not country or not indicator:
            return _empty_result(country_code, indicator_code)

        use_live = api_config.enable_live_data if live is None else live

        fred_point = DataPoint("FRED", None, "N/A", error="Live data disabled")
        wb_point = DataPoint("World Bank", None, "N/A", error="Live data disabled")
        oecd_point = DataPoint("OECD", None, "N/A", error="Live data disabled")

        if use_live:
            wb_point = (
                worldbank_point
                if worldbank_point is not None
                else self.fetch_worldbank(indicator_code, country_code, timeout=timeout)
            )
            if include_fred:
                fred_point = self.fetch_fred(
                    indicator_code, country_code, timeout=timeout
                )
            else:
                fred_point = DataPoint(
                    "FRED", None, "N/A", error="Skipped for bulk sweep"
                )
            oecd_point = self.fetch_oecd(indicator_code, country_code)

        live_values = [
            p.value for p in (fred_point, wb_point, oecd_point) if p.value is not None
        ]

        if live_values:
            source_mode = MODE_LIVE
            fred_value = _round(fred_point.value, indicator.decimal_places)
            wb_value = _round(wb_point.value, indicator.decimal_places)
            oecd_value = _round(oecd_point.value, indicator.decimal_places)
            consensus = round(sum(live_values) / len(live_values), indicator.decimal_places)
            period = next(
                (p.period for p in (wb_point, fred_point, oecd_point)
                 if p.value is not None and p.period != "N/A"),
                "N/A",
            )
            source_note = ", ".join(
                f"{p.source} ({p.period})"
                for p in (fred_point, wb_point, oecd_point)
                if p.value is not None
            )
            confidence_level, confidence_desc = self._calculate_confidence(live_values)
            source_count = len(live_values)
        else:
            source_mode = MODE_MODELLED
            fred_raw, wb_raw, oecd_raw = self._modelled_values(indicator_code, country)
            fred_value = _round(fred_raw, indicator.decimal_places)
            wb_value = _round(wb_raw, indicator.decimal_places)
            oecd_value = _round(oecd_raw, indicator.decimal_places)
            consensus = round(
                (fred_value + wb_value + oecd_value) / 3, indicator.decimal_places
            )
            quarter = (datetime.now().month - 1) // 3 + 1
            period = f"{datetime.now().year}-Q{quarter}"
            reason = wb_point.error or "no live coverage"
            source_note = f"Regional baseline model ({reason})"
            confidence_level, confidence_desc = self._calculate_confidence(
                [fred_value, wb_value, oecd_value]
            )
            source_count = 3

        assessment_label, assessment_desc = get_assessment(indicator_code, consensus)

        return TriangulatedData(
            country_code=country_code,
            country_name=country.name,
            region=country.region,
            income_level=country.income_level,
            indicator_code=indicator_code,
            indicator_name=indicator.display_name,
            unit=indicator.unit,
            fred_value=fred_value,
            worldbank_value=wb_value,
            oecd_value=oecd_value,
            consensus_value=consensus,
            confidence_level=confidence_level,
            confidence_description=confidence_desc,
            assessment_label=assessment_label,
            assessment_description=assessment_desc,
            period=period,
            source_count=source_count,
            source_mode=source_mode,
            source_note=source_note,
        )

    # -------------------------------------------------------------------------
    # Bulk sweeps
    # -------------------------------------------------------------------------
    def fetch_many(
        self,
        indicator_code: str,
        country_codes: List[str],
        live: Optional[bool] = None
    ) -> List[TriangulatedData]:
        """
        Fetch an indicator for many countries.

        Bulk sweeps use the batched World Bank endpoint only. FRED has no batch
        API, and issuing one request per country would make regional and global
        views unusable on free-tier CPU.

        To keep a result set comparable, live and modelled values are not mixed:
        if at least one country resolves live, only live rows are returned. If
        none resolve, every country falls back to the model.
        """
        use_live = api_config.enable_live_data if live is None else live
        codes = [c for c in country_codes if c in COUNTRIES]
        if not codes:
            return []

        if not use_live:
            return [
                self.triangulate(indicator_code, code, live=False) for code in codes
            ]

        wb_points = self.fetch_worldbank_batch(
            indicator_code, codes, timeout=api_config.bulk_timeout
        )
        resolved = [c for c in codes if wb_points.get(c) and wb_points[c].value is not None]

        if resolved:
            logger.info(
                f"Live sweep for {indicator_code}: {len(resolved)}/{len(codes)} "
                f"countries resolved from World Bank"
            )
            return [
                self.triangulate(
                    indicator_code,
                    code,
                    live=True,
                    worldbank_point=wb_points[code],
                    timeout=api_config.bulk_timeout,
                    include_fred=False,
                )
                for code in resolved
            ]

        logger.info(
            f"Live sweep for {indicator_code} returned nothing; using modelled values"
        )
        return [self.triangulate(indicator_code, code, live=False) for code in codes]

    def get_region_data(
        self,
        indicator_code: str,
        region: str,
        live: Optional[bool] = None
    ) -> List[TriangulatedData]:
        """Get data for every country in a region, ranked."""
        results = self.fetch_many(indicator_code, REGIONS.get(region, []), live=live)
        return _sort_by_indicator(results, indicator_code)

    def get_global_ranking(
        self,
        indicator_code: str,
        limit: int = 20,
        live: Optional[bool] = None
    ) -> List[TriangulatedData]:
        """Get the global ranking for an indicator."""
        codes = [c for c in COUNTRIES if c != "EUU"]
        results = self.fetch_many(indicator_code, codes, live=live)
        return _sort_by_indicator(results, indicator_code)[:limit]


# =============================================================================
# HELPERS
# =============================================================================
def _parse_float(value) -> Optional[float]:
    """Coerce an API value to float, returning None when it is not numeric."""
    if value is None or value == "" or value == ".":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    # Guard against NaN/inf sneaking into comparisons and sorts.
    if parsed != parsed or parsed in (float("inf"), float("-inf")):
        return None
    return parsed


def _within_range(value: float, indicator) -> bool:
    """Reject observations outside an indicator's plausible bounds."""
    low, high = indicator.value_range
    return low <= value <= high


def _round(value: Optional[float], places: int) -> Optional[float]:
    """Round a value, passing None through."""
    return None if value is None else round(value, places)


def _worldbank_point(series: List[Tuple[str, float]], indicator) -> DataPoint:
    """
    Turn a country's World Bank observations into a single DataPoint.

    Most indicators are already expressed as the rate we display, so the latest
    valid observation is used. Level series flagged with ``worldbank_derive_yoy``
    are converted to an annual percentage change from the two newest points.
    """
    if indicator.worldbank_derive_yoy:
        if len(series) < 2:
            return DataPoint(
                "World Bank", None, "N/A", error="Need two periods to derive change"
            )
        (latest_date, latest), (prior_date, prior) = series[0], series[1]
        if prior == 0:
            return DataPoint("World Bank", None, "N/A", error="Prior period is zero")
        change = ((latest - prior) / abs(prior)) * 100.0
        if indicator.worldbank_invert_yoy:
            change = -change
        if not _within_range(change, indicator):
            return DataPoint(
                "World Bank", None, "N/A", error="Derived change out of range"
            )
        return DataPoint("World Bank", change, f"{prior_date}-{latest_date}")

    for date, value in series:
        if _within_range(value, indicator):
            return DataPoint("World Bank", value, date)

    return DataPoint("World Bank", None, "N/A", error="All observations out of range")


def _sort_by_indicator(
    results: List[TriangulatedData],
    indicator_code: str
) -> List[TriangulatedData]:
    """Sort results best-first according to the indicator's direction."""
    indicator = INDICATORS.get(indicator_code)
    reverse = True
    if indicator and indicator.higher_is_better is not None:
        reverse = indicator.higher_is_better
    usable = [r for r in results if r.consensus_value is not None]
    usable.sort(key=lambda r: r.consensus_value, reverse=reverse)
    return usable


def _empty_result(country_code: str, indicator_code: str) -> TriangulatedData:
    """Build a placeholder result for an unknown country or indicator."""
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
        source_count=0,
        source_mode=MODE_MODELLED,
        source_note="Invalid request",
    )


# Global instance
data_fetcher = DataFetcher()


# =============================================================================
# CACHING
# =============================================================================
# Hour-bucketed cache shared by single lookups and bulk sweeps, so a regional
# sweep warms the cache for the individual countries it covered. Replaces the
# previous lru_cache, which could not be primed from the bulk path.
_cache: Dict[Tuple[str, str, bool, str], TriangulatedData] = {}
_cache_lock = threading.Lock()
_CACHE_MAX_ENTRIES = 4000


def _cache_bucket() -> str:
    """Current hour, used to expire cached values."""
    return datetime.now().strftime("%Y%m%d%H")


def _cache_key(indicator_code: str, country_code: str, live: bool) -> Tuple:
    return (indicator_code, country_code, live, _cache_bucket())


def cache_put(result: TriangulatedData, live: bool) -> None:
    """Store a result so later lookups reuse it."""
    with _cache_lock:
        if len(_cache) >= _CACHE_MAX_ENTRIES:
            _cache.clear()
        _cache[_cache_key(result.indicator_code, result.country_code, live)] = result


def get_data(
    indicator_code: str,
    country_code: str,
    live: Optional[bool] = None
) -> TriangulatedData:
    """Get triangulated data for one country, cached for the current hour."""
    use_live = api_config.enable_live_data if live is None else live
    key = _cache_key(indicator_code, country_code, use_live)

    with _cache_lock:
        cached = _cache.get(key)
    if cached is not None:
        return cached

    result = data_fetcher.triangulate(indicator_code, country_code, live=use_live)
    cache_put(result, use_live)
    return result


def get_many(
    indicator_code: str,
    country_codes: List[str],
    live: Optional[bool] = None
) -> List[TriangulatedData]:
    """Bulk fetch that also warms the single-lookup cache."""
    use_live = api_config.enable_live_data if live is None else live
    results = data_fetcher.fetch_many(indicator_code, country_codes, live=use_live)
    for result in results:
        cache_put(result, use_live)
    return results


def clear_cache() -> None:
    """Drop all cached results."""
    with _cache_lock:
        _cache.clear()


def cache_size() -> int:
    """Number of cached entries."""
    with _cache_lock:
        return len(_cache)
