"""
Utility Functions
=================
Helper functions for the application.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime


def format_percentage(value: Optional[float], decimals: int = 2) -> str:
    """Format a value as a percentage string."""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_currency(value: Optional[float], currency: str = "USD") -> str:
    """Format a value as currency."""
    if value is None:
        return "N/A"
    
    symbols = {
        "USD": "$",
        "EUR": "E",
        "GBP": "L",
        "JPY": "Y",
        "CNY": "Y",
        "INR": "R",
    }
    symbol = symbols.get(currency, "$")
    return f"{symbol}{value:,.0f}"


def format_large_number(value: float) -> str:
    """Format large numbers with K, M, B suffixes."""
    if abs(value) >= 1e12:
        return f"{value/1e12:.2f}T"
    elif abs(value) >= 1e9:
        return f"{value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"{value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.2f}K"
    else:
        return f"{value:.2f}"


def get_confidence_emoji(confidence: str) -> str:
    """Get emoji for confidence level."""
    emojis = {
        "high": "🟢",
        "medium": "🟡",
        "single_source": "🟠",
        "low": "🔴",
        "no_data": "⚪",
    }
    return emojis.get(confidence, "⚪")


def get_confidence_color(confidence: str) -> str:
    """Get hex color for confidence level."""
    colors = {
        "high": "#28a745",
        "medium": "#ffc107",
        "single_source": "#fd7e14",
        "low": "#dc3545",
        "no_data": "#6c757d",
    }
    return colors.get(confidence, "#6c757d")


def get_assessment_emoji(assessment: str) -> str:
    """Get emoji for assessment level."""
    assessment_lower = assessment.lower()
    
    positive = ["strong", "good", "excellent", "healthy", "tight", "low", "surplus", "optimistic", "boom", "growth", "appreciation"]
    negative = ["weak", "high", "critical", "crisis", "contraction", "deficit", "pessimistic", "depreciation"]
    
    for word in positive:
        if word in assessment_lower:
            return "📈"
    
    for word in negative:
        if word in assessment_lower:
            return "📉"
    
    return "➡️"


def get_region_emoji(region: str) -> str:
    """Get emoji for region."""
    emojis = {
        "North America": "🌎",
        "South America": "🌎",
        "Europe - Western": "🇪🇺",
        "Europe - Northern": "🇪🇺",
        "Europe - Southern": "🇪🇺",
        "Europe - Eastern": "🇪🇺",
        "Europe": "🇪🇺",
        "Russia and CIS": "🌍",
        "Asia - East": "🌏",
        "Asia - South": "🌏",
        "Asia - Southeast": "🌏",
        "Asia": "🌏",
        "Middle East": "🌍",
        "Africa - North": "🌍",
        "Africa - Sub-Saharan": "🌍",
        "Africa": "🌍",
        "Oceania": "🌏",
        "Aggregates": "🌐",
    }
    return emojis.get(region, "🌐")


def get_income_level_display(income_level: str) -> str:
    """Get display text for income level."""
    displays = {
        "high": "High Income",
        "upper_middle": "Upper Middle Income",
        "lower_middle": "Lower Middle Income",
        "low": "Low Income",
    }
    return displays.get(income_level, income_level.replace("_", " ").title())


def get_current_quarter() -> str:
    """Get current quarter string."""
    now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year}-Q{quarter}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def create_source_citation(
    fred: Optional[float],
    wb: Optional[float],
    oecd: Optional[float]
) -> str:
    """Create formatted source citation string."""
    sources = []
    if fred is not None:
        sources.append(f"FRED: {fred:.2f}")
    if wb is not None:
        sources.append(f"World Bank: {wb:.2f}")
    if oecd is not None:
        sources.append(f"OECD: {oecd:.2f}")
    
    if not sources:
        return "No data available"
    
    return " | ".join(sources)


def calculate_change(current: float, previous: float) -> Tuple[float, str]:
    """Calculate percentage change and direction."""
    if previous == 0:
        return 0.0, "unchanged"
    
    change = ((current - previous) / abs(previous)) * 100
    
    if change > 0.5:
        direction = "increased"
    elif change < -0.5:
        direction = "decreased"
    else:
        direction = "unchanged"
    
    return change, direction


def validate_country_code(code: str) -> bool:
    """Validate if a country code exists."""
    from countries import COUNTRIES
    return code in COUNTRIES


def validate_indicator_code(code: str) -> bool:
    """Validate if an indicator code exists."""
    from indicators import INDICATORS
    return code in INDICATORS