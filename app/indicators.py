"""
Indicator Configuration
=======================
Configuration for all 12 macroeconomic indicators.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class IndicatorConfig:
    """Configuration for a macroeconomic indicator."""
    code: str
    name: str
    display_name: str
    short_name: str
    unit: str
    description: str
    icon: str
    higher_is_better: Optional[bool]
    decimal_places: int
    color: str


INDICATORS: Dict[str, IndicatorConfig] = {
    "gdp_growth": IndicatorConfig(
        code="gdp_growth",
        name="GDP Growth Rate",
        display_name="GDP Growth",
        short_name="GDP",
        unit="%",
        description="Annual percentage change in real gross domestic product",
        icon="📈",
        higher_is_better=True,
        decimal_places=2,
        color="#2ecc71"
    ),
    "inflation": IndicatorConfig(
        code="inflation",
        name="Inflation Rate",
        display_name="Inflation",
        short_name="CPI",
        unit="%",
        description="Annual percentage change in consumer price index",
        icon="💰",
        higher_is_better=False,
        decimal_places=2,
        color="#e74c3c"
    ),
    "unemployment": IndicatorConfig(
        code="unemployment",
        name="Unemployment Rate",
        display_name="Unemployment",
        short_name="UE",
        unit="%",
        description="Percentage of labor force without employment",
        icon="👥",
        higher_is_better=False,
        decimal_places=2,
        color="#9b59b6"
    ),
    "interest_rate": IndicatorConfig(
        code="interest_rate",
        name="Policy Interest Rate",
        display_name="Interest Rate",
        short_name="IR",
        unit="%",
        description="Central bank benchmark policy rate",
        icon="🏦",
        higher_is_better=None,
        decimal_places=2,
        color="#3498db"
    ),
    "gdp_per_capita": IndicatorConfig(
        code="gdp_per_capita",
        name="GDP Per Capita",
        display_name="GDP Per Capita",
        short_name="GDPPC",
        unit="USD",
        description="Gross domestic product divided by total population",
        icon="💵",
        higher_is_better=True,
        decimal_places=0,
        color="#1abc9c"
    ),
    "current_account": IndicatorConfig(
        code="current_account",
        name="Current Account Balance",
        display_name="Current Account",
        short_name="CA",
        unit="% of GDP",
        description="Sum of trade balance, net income, and net transfers",
        icon="⚖️",
        higher_is_better=None,
        decimal_places=2,
        color="#f39c12"
    ),
    "government_debt": IndicatorConfig(
        code="government_debt",
        name="Government Debt",
        display_name="Public Debt",
        short_name="Debt",
        unit="% of GDP",
        description="Total government debt as percentage of GDP",
        icon="📊",
        higher_is_better=False,
        decimal_places=1,
        color="#e67e22"
    ),
    "fdi_inflows": IndicatorConfig(
        code="fdi_inflows",
        name="Foreign Direct Investment Inflows",
        display_name="FDI Inflows",
        short_name="FDI",
        unit="% of GDP",
        description="Net inflows of foreign direct investment",
        icon="🌐",
        higher_is_better=True,
        decimal_places=2,
        color="#27ae60"
    ),
    "exchange_rate_change": IndicatorConfig(
        code="exchange_rate_change",
        name="Exchange Rate Change",
        display_name="Currency Change",
        short_name="FX",
        unit="%",
        description="Annual percentage change in exchange rate versus USD",
        icon="💱",
        higher_is_better=None,
        decimal_places=2,
        color="#8e44ad"
    ),
    "industrial_production": IndicatorConfig(
        code="industrial_production",
        name="Industrial Production Growth",
        display_name="Industrial Production",
        short_name="IP",
        unit="%",
        description="Annual growth rate of industrial output",
        icon="🏭",
        higher_is_better=True,
        decimal_places=2,
        color="#34495e"
    ),
    "consumer_confidence": IndicatorConfig(
        code="consumer_confidence",
        name="Consumer Confidence Index",
        display_name="Consumer Confidence",
        short_name="CCI",
        unit="index",
        description="Survey-based measure of household economic sentiment",
        icon="😊",
        higher_is_better=True,
        decimal_places=1,
        color="#16a085"
    ),
    "trade_balance": IndicatorConfig(
        code="trade_balance",
        name="Trade Balance",
        display_name="Trade Balance",
        short_name="TB",
        unit="% of GDP",
        description="Exports minus imports as percentage of GDP",
        icon="🚢",
        higher_is_better=None,
        decimal_places=2,
        color="#2980b9"
    ),
}


# Assessment thresholds
THRESHOLDS: Dict[str, List[Tuple[float, str, str]]] = {
    "gdp_growth": [
        (5.0, "Strong", "Robust economic expansion"),
        (3.0, "Good", "Healthy economic growth"),
        (1.5, "Moderate", "Sluggish but positive growth"),
        (0.0, "Weak", "Near-stagnation conditions"),
        (float("-inf"), "Contraction", "Economy in recession"),
    ],
    "inflation": [
        (2.0, "Low", "Well-controlled price stability"),
        (3.5, "Target", "Near central bank targets"),
        (6.0, "Elevated", "Above-target inflation"),
        (10.0, "High", "Significant inflationary pressure"),
        (float("inf"), "Critical", "Hyperinflationary risk"),
    ],
    "unemployment": [
        (4.0, "Tight", "Strong labor market"),
        (5.5, "Healthy", "Near full employment"),
        (8.0, "Elevated", "Labor market slack"),
        (12.0, "High", "Significant joblessness"),
        (float("inf"), "Crisis", "Severe unemployment"),
    ],
    "interest_rate": [
        (2.0, "Accommodative", "Stimulative policy"),
        (5.0, "Neutral", "Balanced stance"),
        (8.0, "Restrictive", "Tight conditions"),
        (float("inf"), "Very Tight", "Highly restrictive"),
    ],
    "gdp_per_capita": [
        (40000, "High Income", "Advanced economy"),
        (15000, "Upper Middle", "Emerging market"),
        (4000, "Lower Middle", "Developing economy"),
        (float("-inf"), "Low Income", "Least developed"),
    ],
    "current_account": [
        (5.0, "Large Surplus", "Strong external position"),
        (2.0, "Surplus", "Positive external balance"),
        (-2.0, "Balanced", "Sustainable position"),
        (-5.0, "Deficit", "External financing needs"),
        (float("-inf"), "Large Deficit", "External vulnerability"),
    ],
    "government_debt": [
        (40.0, "Low", "Strong fiscal position"),
        (60.0, "Moderate", "Manageable debt"),
        (90.0, "High", "Elevated debt"),
        (120.0, "Very High", "Sustainability concerns"),
        (float("inf"), "Critical", "Severe fiscal stress"),
    ],
    "fdi_inflows": [
        (5.0, "Excellent", "Highly attractive"),
        (3.0, "Strong", "Good investment climate"),
        (1.5, "Moderate", "Average attractiveness"),
        (float("-inf"), "Weak", "Limited investment"),
    ],
    "exchange_rate_change": [
        (10.0, "Strong Appreciation", "Currency strengthening"),
        (3.0, "Appreciation", "Currency gaining"),
        (-3.0, "Stable", "Limited movement"),
        (-10.0, "Depreciation", "Currency losing value"),
        (float("-inf"), "Sharp Depreciation", "Significant weakness"),
    ],
    "industrial_production": [
        (6.0, "Boom", "Strong expansion"),
        (3.0, "Growth", "Healthy activity"),
        (1.0, "Moderate", "Slow growth"),
        (0.0, "Stagnant", "Flat output"),
        (float("-inf"), "Contraction", "Industrial decline"),
    ],
    "consumer_confidence": [
        (105.0, "Optimistic", "Strong sentiment"),
        (100.0, "Neutral", "Balanced outlook"),
        (95.0, "Cautious", "Consumer uncertainty"),
        (float("-inf"), "Pessimistic", "Weak sentiment"),
    ],
    "trade_balance": [
        (8.0, "Large Surplus", "Export-oriented"),
        (3.0, "Surplus", "Positive trade position"),
        (-3.0, "Balanced", "Sustainable position"),
        (-8.0, "Deficit", "Import-dependent"),
        (float("-inf"), "Large Deficit", "Trade imbalance"),
    ],
}


def get_assessment(indicator_code: str, value: float) -> Tuple[str, str]:
    """Get assessment label and description for an indicator value."""
    if indicator_code not in THRESHOLDS:
        return "Moderate", "Within normal range"
    
    thresholds = THRESHOLDS[indicator_code]
    indicator = INDICATORS.get(indicator_code)
    
    if indicator and indicator.higher_is_better is True:
        for threshold, label, desc in thresholds:
            if value >= threshold:
                return label, desc
    elif indicator and indicator.higher_is_better is False:
        for threshold, label, desc in thresholds:
            if value <= threshold:
                return label, desc
    else:
        for threshold, label, desc in thresholds:
            if value >= threshold:
                return label, desc
    
    return "Moderate", "Within normal range"


def format_value(indicator_code: str, value: float) -> str:
    """Format a value according to indicator specifications."""
    indicator = INDICATORS.get(indicator_code)
    if not indicator:
        return str(value)
    
    if indicator_code == "gdp_per_capita":
        return f"${value:,.0f}"
    elif indicator_code == "consumer_confidence":
        return f"{value:.1f}"
    elif indicator_code == "exchange_rate_change":
        return f"{value:+.2f}%"
    else:
        return f"{value:.{indicator.decimal_places}f}%"


def get_indicator_options() -> Dict[str, str]:
    """Get indicator code to display name mapping for UI."""
    return {code: f"{ind.icon} {ind.display_name}" for code, ind in INDICATORS.items()}