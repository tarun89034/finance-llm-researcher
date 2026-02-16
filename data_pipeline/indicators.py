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
    unit: str
    description: str
    higher_is_better: Optional[bool]
    fred_series_template: Optional[str]
    worldbank_indicator: Optional[str]
    oecd_dataset: Optional[str]
    value_range: Tuple[float, float]
    decimal_places: int
    format_template: str


INDICATORS: Dict[str, IndicatorConfig] = {
    
    "gdp_growth": IndicatorConfig(
        code="gdp_growth",
        name="GDP Growth Rate",
        display_name="GDP Growth",
        unit="%",
        description="Annual percentage change in real gross domestic product",
        higher_is_better=True,
        fred_series_template="{country}GDPRQPSMEI",
        worldbank_indicator="NY.GDP.MKTP.KD.ZG",
        oecd_dataset="QNA",
        value_range=(-15.0, 20.0),
        decimal_places=2,
        format_template="{value:.2f}%"
    ),
    
    "inflation": IndicatorConfig(
        code="inflation",
        name="Inflation Rate",
        display_name="Inflation",
        unit="%",
        description="Annual percentage change in consumer price index",
        higher_is_better=False,
        fred_series_template="{country}CPIALLMINMEI",
        worldbank_indicator="FP.CPI.TOTL.ZG",
        oecd_dataset="PRICES_CPI",
        value_range=(-5.0, 100.0),
        decimal_places=2,
        format_template="{value:.2f}%"
    ),
    
    "unemployment": IndicatorConfig(
        code="unemployment",
        name="Unemployment Rate",
        display_name="Unemployment",
        unit="%",
        description="Percentage of labor force without employment",
        higher_is_better=False,
        fred_series_template="LMUNRRTT{country}M156S",
        worldbank_indicator="SL.UEM.TOTL.ZS",
        oecd_dataset="LFS_SEXAGE_I_R",
        value_range=(0.0, 35.0),
        decimal_places=2,
        format_template="{value:.2f}%"
    ),
    
    "interest_rate": IndicatorConfig(
        code="interest_rate",
        name="Policy Interest Rate",
        display_name="Interest Rate",
        unit="%",
        description="Central bank benchmark policy rate",
        higher_is_better=None,
        fred_series_template="INTDSR{country}M193N",
        worldbank_indicator="FR.INR.RINR",
        oecd_dataset="MEI_FIN",
        value_range=(0.0, 50.0),
        decimal_places=2,
        format_template="{value:.2f}%"
    ),
    
    "gdp_per_capita": IndicatorConfig(
        code="gdp_per_capita",
        name="GDP Per Capita",
        display_name="GDP Per Capita",
        unit="USD",
        description="Gross domestic product divided by total population",
        higher_is_better=True,
        fred_series_template=None,
        worldbank_indicator="NY.GDP.PCAP.CD",
        oecd_dataset=None,
        value_range=(200.0, 150000.0),
        decimal_places=0,
        format_template="${value:,.0f}"
    ),
    
    "current_account": IndicatorConfig(
        code="current_account",
        name="Current Account Balance",
        display_name="Current Account",
        unit="% of GDP",
        description="Sum of trade balance, net income, and net transfers as percentage of GDP",
        higher_is_better=None,
        fred_series_template=None,
        worldbank_indicator="BN.CAB.XOKA.GD.ZS",
        oecd_dataset=None,
        value_range=(-30.0, 40.0),
        decimal_places=2,
        format_template="{value:.2f}%"
    ),
    
    "government_debt": IndicatorConfig(
        code="government_debt",
        name="Government Debt",
        display_name="Public Debt",
        unit="% of GDP",
        description="Total government debt as percentage of GDP",
        higher_is_better=False,
        fred_series_template=None,
        worldbank_indicator="GC.DOD.TOTL.GD.ZS",
        oecd_dataset=None,
        value_range=(0.0, 300.0),
        decimal_places=1,
        format_template="{value:.1f}%"
    ),
    
    "fdi_inflows": IndicatorConfig(
        code="fdi_inflows",
        name="Foreign Direct Investment Inflows",
        display_name="FDI Inflows",
        unit="% of GDP",
        description="Net inflows of foreign direct investment as percentage of GDP",
        higher_is_better=True,
        fred_series_template=None,
        worldbank_indicator="BX.KLT.DINV.WD.GD.ZS",
        oecd_dataset=None,
        value_range=(-10.0, 30.0),
        decimal_places=2,
        format_template="{value:.2f}%"
    ),
    
    "exchange_rate_change": IndicatorConfig(
        code="exchange_rate_change",
        name="Exchange Rate Change",
        display_name="Currency Change",
        unit="%",
        description="Annual percentage change in exchange rate versus USD (positive = appreciation)",
        higher_is_better=None,
        fred_series_template=None,
        worldbank_indicator="PA.NUS.FCRF",
        oecd_dataset=None,
        value_range=(-50.0, 50.0),
        decimal_places=2,
        format_template="{value:+.2f}%"
    ),
    
    "industrial_production": IndicatorConfig(
        code="industrial_production",
        name="Industrial Production Growth",
        display_name="Industrial Production",
        unit="%",
        description="Annual growth rate of industrial output",
        higher_is_better=True,
        fred_series_template="{country}PRMNTO01GYSAM",
        worldbank_indicator="NV.IND.TOTL.KD.ZG",
        oecd_dataset="MEI",
        value_range=(-30.0, 30.0),
        decimal_places=2,
        format_template="{value:.2f}%"
    ),
    
    "consumer_confidence": IndicatorConfig(
        code="consumer_confidence",
        name="Consumer Confidence Index",
        display_name="Consumer Confidence",
        unit="index",
        description="Survey-based measure of household economic sentiment (100 = neutral)",
        higher_is_better=True,
        fred_series_template=None,
        worldbank_indicator=None,
        oecd_dataset="MEI_CLI",
        value_range=(50.0, 150.0),
        decimal_places=1,
        format_template="{value:.1f}"
    ),
    
    "trade_balance": IndicatorConfig(
        code="trade_balance",
        name="Trade Balance",
        display_name="Trade Balance",
        unit="% of GDP",
        description="Exports minus imports as percentage of GDP",
        higher_is_better=None,
        fred_series_template=None,
        worldbank_indicator="NE.RSB.GNFS.ZS",
        oecd_dataset=None,
        value_range=(-40.0, 50.0),
        decimal_places=2,
        format_template="{value:.2f}%"
    ),
}


# Assessment thresholds for each indicator
ASSESSMENT_THRESHOLDS: Dict[str, Dict[str, List[Tuple[float, str, str]]]] = {
    "gdp_growth": {
        "thresholds": [
            (5.0, "Strong", "Economy showing robust expansion"),
            (3.0, "Good", "Healthy economic growth"),
            (1.5, "Moderate", "Sluggish but positive growth"),
            (0.0, "Weak", "Near-stagnation conditions"),
            (float("-inf"), "Contraction", "Economy in recession"),
        ]
    },
    "inflation": {
        "thresholds": [
            (2.0, "Low", "Well-controlled price stability"),
            (3.5, "Target", "Near central bank targets"),
            (6.0, "Elevated", "Above-target inflation requiring monitoring"),
            (10.0, "High", "Significant inflationary pressure"),
            (float("inf"), "Critical", "Hyperinflationary risk"),
        ]
    },
    "unemployment": {
        "thresholds": [
            (4.0, "Tight", "Strong labor market conditions"),
            (5.5, "Healthy", "Near full employment"),
            (8.0, "Elevated", "Labor market slack present"),
            (12.0, "High", "Significant joblessness"),
            (float("inf"), "Crisis", "Severe unemployment crisis"),
        ]
    },
    "interest_rate": {
        "thresholds": [
            (2.0, "Accommodative", "Highly stimulative monetary policy"),
            (5.0, "Neutral", "Balanced monetary stance"),
            (8.0, "Restrictive", "Tight monetary conditions"),
            (float("inf"), "Very Tight", "Highly restrictive policy"),
        ]
    },
    "gdp_per_capita": {
        "thresholds": [
            (40000, "High Income", "Advanced economy living standards"),
            (15000, "Upper Middle", "Emerging market development level"),
            (4000, "Lower Middle", "Developing economy"),
            (float("-inf"), "Low Income", "Least developed economy"),
        ]
    },
    "current_account": {
        "thresholds": [
            (5.0, "Large Surplus", "Strong external position"),
            (2.0, "Surplus", "Positive external balance"),
            (-2.0, "Balanced", "Sustainable external position"),
            (-5.0, "Deficit", "External financing needs"),
            (float("-inf"), "Large Deficit", "Significant external vulnerability"),
        ]
    },
    "government_debt": {
        "thresholds": [
            (40.0, "Low", "Strong fiscal position"),
            (60.0, "Moderate", "Manageable debt levels"),
            (90.0, "High", "Elevated debt requiring attention"),
            (120.0, "Very High", "Debt sustainability concerns"),
            (float("inf"), "Critical", "Severe fiscal stress"),
        ]
    },
    "fdi_inflows": {
        "thresholds": [
            (5.0, "Excellent", "Highly attractive investment destination"),
            (3.0, "Strong", "Good investment climate"),
            (1.5, "Moderate", "Average investment attractiveness"),
            (float("-inf"), "Weak", "Limited foreign investment"),
        ]
    },
    "exchange_rate_change": {
        "thresholds": [
            (10.0, "Strong Appreciation", "Currency strengthening significantly"),
            (3.0, "Appreciation", "Currency gaining value"),
            (-3.0, "Stable", "Limited currency movement"),
            (-10.0, "Depreciation", "Currency losing value"),
            (float("-inf"), "Sharp Depreciation", "Significant currency weakness"),
        ]
    },
    "industrial_production": {
        "thresholds": [
            (6.0, "Boom", "Strong industrial expansion"),
            (3.0, "Growth", "Healthy manufacturing activity"),
            (1.0, "Moderate", "Slow industrial growth"),
            (0.0, "Stagnant", "Flat industrial output"),
            (float("-inf"), "Contraction", "Industrial decline"),
        ]
    },
    "consumer_confidence": {
        "thresholds": [
            (105.0, "Optimistic", "Strong consumer sentiment"),
            (100.0, "Neutral", "Balanced consumer outlook"),
            (95.0, "Cautious", "Consumer uncertainty"),
            (float("-inf"), "Pessimistic", "Weak consumer sentiment"),
        ]
    },
    "trade_balance": {
        "thresholds": [
            (8.0, "Large Surplus", "Strong export-oriented economy"),
            (3.0, "Surplus", "Positive trade position"),
            (-3.0, "Balanced", "Sustainable trade position"),
            (-8.0, "Deficit", "Import-dependent economy"),
            (float("-inf"), "Large Deficit", "Significant trade imbalance"),
        ]
    },
}


def get_assessment(indicator_code: str, value: float) -> Tuple[str, str]:
    """
    Get assessment label and description for an indicator value.
    
    Args:
        indicator_code: The indicator code
        value: The indicator value
        
    Returns:
        Tuple of (assessment_label, assessment_description)
    """
    if indicator_code not in ASSESSMENT_THRESHOLDS:
        return "Moderate", "Within normal range"
    
    thresholds = ASSESSMENT_THRESHOLDS[indicator_code]["thresholds"]
    indicator = INDICATORS[indicator_code]
    
    # For indicators where higher is better, sort descending
    # For indicators where lower is better, sort ascending
    if indicator.higher_is_better is True:
        for threshold, label, description in thresholds:
            if value >= threshold:
                return label, description
    elif indicator.higher_is_better is False:
        for threshold, label, description in thresholds:
            if value <= threshold:
                return label, description
    else:
        # For neutral indicators, check ranges
        for threshold, label, description in thresholds:
            if value >= threshold:
                return label, description
    
    return "Moderate", "Within normal range"


def format_value(indicator_code: str, value: float) -> str:
    """
    Format a value according to indicator specifications.
    
    Args:
        indicator_code: The indicator code
        value: The value to format
        
    Returns:
        Formatted value string
    """
    if indicator_code not in INDICATORS:
        return str(value)
    
    indicator = INDICATORS[indicator_code]
    return indicator.format_template.format(value=value)


def get_indicator_list() -> List[str]:
    """Get list of all indicator codes."""
    return list(INDICATORS.keys())


def get_indicator_display_names() -> Dict[str, str]:
    """Get mapping of indicator codes to display names."""
    return {code: ind.display_name for code, ind in INDICATORS.items()}