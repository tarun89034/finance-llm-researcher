"""
Visualizations
==============
Plotly charts and graphs for data visualization.
"""

from typing import Dict, List, Optional

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from data_fetcher import TriangulatedData
from indicators import INDICATORS, format_value
from countries import COUNTRIES


def get_confidence_color(confidence: str) -> str:
    """Get color for confidence level."""
    colors = {
        "high": "#28a745",
        "medium": "#ffc107",
        "single_source": "#fd7e14",
        "low": "#dc3545",
        "no_data": "#6c757d",
    }
    return colors.get(confidence, "#6c757d")


def create_region_bar_chart(
    data: List[TriangulatedData],
    indicator_code: str
) -> go.Figure:
    """
    Create horizontal bar chart for regional data.
    
    Args:
        data: List of TriangulatedData objects
        indicator_code: The indicator code
        
    Returns:
        Plotly Figure object
    """
    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Sort by consensus value
    indicator = INDICATORS.get(indicator_code)
    reverse = indicator.higher_is_better if indicator and indicator.higher_is_better is not None else True
    data_sorted = sorted(data, key=lambda x: x.consensus_value or 0, reverse=not reverse)
    
    countries = [d.country_name for d in data_sorted]
    values = [d.consensus_value for d in data_sorted]
    colors = [get_confidence_color(d.confidence_level) for d in data_sorted]
    
    # Format hover text
    hover_texts = []
    for d in data_sorted:
        formatted = format_value(indicator_code, d.consensus_value)
        hover_texts.append(
            f"<b>{d.country_name}</b><br>"
            f"Value: {formatted}<br>"
            f"Confidence: {d.confidence_level.title()}<br>"
            f"Assessment: {d.assessment_label}"
        )
    
    fig = go.Figure(go.Bar(
        x=values,
        y=countries,
        orientation="h",
        marker_color=colors,
        text=[format_value(indicator_code, v) for v in values],
        textposition="outside",
        hovertemplate="%{customdata}<extra></extra>",
        customdata=hover_texts,
    ))
    
    indicator_name = indicator.display_name if indicator else indicator_code
    
    fig.update_layout(
        title=f"{indicator_name} by Country",
        xaxis_title=f"Value ({indicator.unit if indicator else ''})",
        yaxis_title="",
        height=max(400, len(data) * 35),
        margin=dict(l=150, r=80, t=50, b=50),
        showlegend=False,
    )
    
    return fig


def create_global_ranking_chart(
    data: List[TriangulatedData],
    indicator_code: str,
    top_n: int = 15
) -> go.Figure:
    """
    Create bar chart for global rankings.
    
    Args:
        data: List of TriangulatedData objects
        indicator_code: The indicator code
        top_n: Number of top countries to display
        
    Returns:
        Plotly Figure object
    """
    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    data_limited = data[:top_n]
    
    countries = [d.country_name for d in data_limited]
    values = [d.consensus_value for d in data_limited]
    regions = [d.region for d in data_limited]
    
    # Assign colors by region
    unique_regions = list(set(regions))
    color_palette = px.colors.qualitative.Set2
    region_colors = {r: color_palette[i % len(color_palette)] for i, r in enumerate(unique_regions)}
    colors = [region_colors[r] for r in regions]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=countries,
        orientation="h",
        marker_color=colors,
        text=[format_value(indicator_code, v) for v in values],
        textposition="outside",
    ))
    
    indicator = INDICATORS.get(indicator_code)
    indicator_name = indicator.display_name if indicator else indicator_code
    
    fig.update_layout(
        title=f"Top {top_n} Countries by {indicator_name}",
        xaxis_title=f"Value ({indicator.unit if indicator else ''})",
        yaxis_title="",
        height=500,
        yaxis=dict(categoryorder="total ascending"),
        margin=dict(l=150, r=80, t=50, b=50),
    )
    
    return fig


def create_comparison_chart(
    data: List[TriangulatedData],
    indicator_code: str
) -> go.Figure:
    """
    Create grouped bar chart comparing countries across data sources.
    
    Args:
        data: List of TriangulatedData objects
        indicator_code: The indicator code
        
    Returns:
        Plotly Figure object
    """
    if not data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    countries = [d.country_name for d in data]
    fred_values = [d.fred_value for d in data]
    wb_values = [d.worldbank_value for d in data]
    oecd_values = [d.oecd_value for d in data]
    consensus_values = [d.consensus_value for d in data]
    
    fig = go.Figure()
    
    # Add bars for each source
    fig.add_trace(go.Bar(
        name="FRED",
        x=countries,
        y=fred_values,
        marker_color="#1f77b4",
    ))
    
    fig.add_trace(go.Bar(
        name="World Bank",
        x=countries,
        y=wb_values,
        marker_color="#2ca02c",
    ))
    
    fig.add_trace(go.Bar(
        name="OECD",
        x=countries,
        y=oecd_values,
        marker_color="#ff7f0e",
    ))
    
    # Add consensus line
    fig.add_trace(go.Scatter(
        name="Consensus",
        x=countries,
        y=consensus_values,
        mode="markers+lines",
        marker=dict(size=12, color="#d62728", symbol="diamond"),
        line=dict(color="#d62728", width=2, dash="dash"),
    ))
    
    indicator = INDICATORS.get(indicator_code)
    indicator_name = indicator.display_name if indicator else indicator_code
    
    fig.update_layout(
        title=f"{indicator_name} Comparison by Data Source",
        xaxis_title="Country",
        yaxis_title=f"Value ({indicator.unit if indicator else ''})",
        barmode="group",
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
    )
    
    return fig


def create_multi_indicator_radar(
    data: Dict[str, Optional[float]],
    country_name: str
) -> go.Figure:
    """
    Create radar chart for multiple indicators.
    
    Args:
        data: Dictionary mapping indicator codes to values
        country_name: Name of the country
        
    Returns:
        Plotly Figure object
    """
    indicators = list(data.keys())
    values = list(data.values())
    
    # Normalize values to 0-100 scale for radar chart
    normalized = []
    for indicator_code, value in zip(indicators, values):
        if value is None:
            normalized.append(0)
            continue
        
        # Normalize based on indicator type
        if indicator_code == "gdp_growth":
            norm = min(100, max(0, (value + 5) * 6.67))
        elif indicator_code == "inflation":
            norm = min(100, max(0, 100 - value * 5))
        elif indicator_code == "unemployment":
            norm = min(100, max(0, 100 - value * 4))
        elif indicator_code == "gdp_per_capita":
            norm = min(100, max(0, value / 1000))
        elif indicator_code == "consumer_confidence":
            norm = min(100, max(0, value))
        else:
            norm = 50
        
        normalized.append(norm)
    
    # Get display names
    display_names = [
        INDICATORS[code].short_name if code in INDICATORS else code
        for code in indicators
    ]
    
    fig = go.Figure(go.Scatterpolar(
        r=normalized,
        theta=display_names,
        fill="toself",
        name=country_name,
        line_color="#3498db",
        fillcolor="rgba(52, 152, 219, 0.3)",
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
            )
        ),
        showlegend=True,
        title=f"Economic Profile: {country_name}",
        height=450,
    )
    
    return fig


def create_metric_gauge(
    value: Optional[float],
    indicator_code: str,
    country_name: str
) -> go.Figure:
    """
    Create gauge chart for a single metric.
    
    Args:
        value: The metric value
        indicator_code: The indicator code
        country_name: Name of the country
        
    Returns:
        Plotly Figure object
    """
    if value is None:
        fig = go.Figure()
        fig.add_annotation(
            text="No data",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    indicator = INDICATORS.get(indicator_code)
    indicator_name = indicator.display_name if indicator else indicator_code
    
    # Define gauge ranges based on indicator
    ranges = {
        "gdp_growth": {"min": -5, "max": 15, "good": [2, 8]},
        "inflation": {"min": 0, "max": 20, "good": [1, 4]},
        "unemployment": {"min": 0, "max": 25, "good": [2, 6]},
        "interest_rate": {"min": 0, "max": 20, "good": [2, 6]},
        "consumer_confidence": {"min": 70, "max": 130, "good": [100, 115]},
    }
    
    r = ranges.get(indicator_code, {"min": 0, "max": 100, "good": [30, 70]})
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": f"{country_name}<br>{indicator_name}"},
        number={"suffix": indicator.unit if indicator else ""},
        gauge={
            "axis": {"range": [r["min"], r["max"]]},
            "bar": {"color": "#3498db"},
            "steps": [
                {"range": [r["min"], r["good"][0]], "color": "#ffcccc"},
                {"range": r["good"], "color": "#ccffcc"},
                {"range": [r["good"][1], r["max"]], "color": "#ffcccc"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": value,
            },
        },
    ))
    
    fig.update_layout(height=300)
    return fig


def create_source_comparison_pie(data: TriangulatedData) -> go.Figure:
    """
    Create pie chart showing data source contributions.
    
    Args:
        data: TriangulatedData object
        
    Returns:
        Plotly Figure object
    """
    sources = ["FRED", "World Bank", "OECD"]
    values = [
        data.fred_value or 0,
        data.worldbank_value or 0,
        data.oecd_value or 0,
    ]
    
    # Calculate relative contributions
    total = sum(values)
    if total == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data", x=0.5, y=0.5, showarrow=False)
        return fig
    
    fig = go.Figure(go.Pie(
        labels=sources,
        values=values,
        hole=0.4,
        marker_colors=["#1f77b4", "#2ca02c", "#ff7f0e"],
    ))
    
    fig.update_layout(
        title=f"Data Source Comparison: {data.country_name}",
        height=350,
    )
    
    return fig