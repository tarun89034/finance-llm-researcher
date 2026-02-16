"""
Training Data Builder
=====================
Builds training dataset from generated macroeconomic data.
"""

import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import config
from .countries import COUNTRIES, REGIONS
from .indicators import INDICATORS, format_value
from .data_generator import DataGenerator, MacroeconomicDataPoint


# System instruction for the model
SYSTEM_INSTRUCTION = """You are a senior financial analyst providing comprehensive macroeconomic analysis for 80+ countries worldwide. Your analysis must:

1. Present data from multiple authoritative sources (FRED, World Bank, OECD)
2. Calculate and present consensus values from triangulated data
3. Assess confidence levels based on source agreement
4. Provide risk or quality assessments appropriate to each indicator
5. Contextualize findings within regional and income-level frameworks
6. Cover all major economic regions: North America, South America, Europe, Russia and CIS, Asia, Middle East, Africa, and Oceania

You analyze 12 key macroeconomic indicators:
- GDP Growth Rate
- Inflation Rate
- Unemployment Rate
- Policy Interest Rate
- GDP Per Capita
- Current Account Balance
- Government Debt
- Foreign Direct Investment Inflows
- Exchange Rate Change
- Industrial Production Growth
- Consumer Confidence Index
- Trade Balance"""


# Question templates for each indicator
QUESTION_TEMPLATES: Dict[str, List[str]] = {
    "gdp_growth": [
        "What is the GDP growth rate for {}?",
        "What is the current economic growth in {}?",
        "How is {}'s economy growing?",
        "Tell me about {}'s GDP growth rate.",
        "What is the economic growth rate for {}?",
    ],
    "inflation": [
        "What is the inflation rate in {}?",
        "How high is inflation in {}?",
        "What is the current inflation for {}?",
        "Tell me about {}'s inflation rate.",
        "What is the CPI inflation in {}?",
    ],
    "unemployment": [
        "What is the unemployment rate in {}?",
        "How is the job market in {}?",
        "What is the jobless rate in {}?",
        "Tell me about unemployment in {}.",
        "What is the labor market situation in {}?",
    ],
    "interest_rate": [
        "What is the interest rate in {}?",
        "What is the central bank rate for {}?",
        "What is the policy rate in {}?",
        "Tell me about {}'s monetary policy.",
        "What is the benchmark interest rate in {}?",
    ],
    "gdp_per_capita": [
        "What is the GDP per capita in {}?",
        "What is the income level in {}?",
        "How wealthy is {} on a per-person basis?",
        "What is the economic output per capita in {}?",
    ],
    "current_account": [
        "What is {}'s current account balance?",
        "What is the external balance situation in {}?",
        "Does {} have a current account surplus or deficit?",
        "Tell me about {}'s current account position.",
    ],
    "government_debt": [
        "What is the government debt level in {}?",
        "How high is public debt in {}?",
        "What is {}'s debt-to-GDP ratio?",
        "Tell me about {}'s fiscal debt situation.",
    ],
    "fdi_inflows": [
        "What are the FDI inflows to {}?",
        "How much foreign direct investment does {} receive?",
        "What is {}'s foreign investment attractiveness?",
        "Tell me about FDI in {}.",
    ],
    "exchange_rate_change": [
        "How has {}'s currency performed?",
        "What is the exchange rate trend in {}?",
        "Has {}'s currency appreciated or depreciated?",
        "Tell me about {}'s currency movement.",
    ],
    "industrial_production": [
        "What is the industrial production growth in {}?",
        "How is {}'s manufacturing sector performing?",
        "What is the industrial output trend in {}?",
        "Tell me about {}'s industrial production.",
    ],
    "consumer_confidence": [
        "What is consumer confidence in {}?",
        "How do consumers feel about {}'s economy?",
        "What is household sentiment in {}?",
        "Tell me about consumer outlook in {}.",
    ],
    "trade_balance": [
        "What is {}'s trade balance?",
        "Does {} have a trade surplus or deficit?",
        "What is the trade position for {}?",
        "Tell me about {}'s import-export balance.",
    ],
}

# Comparison pairs for generating comparison questions
COMPARISON_PAIRS: List[Tuple[str, str]] = [
    # Major economies
    ("USA", "CHN"), ("USA", "IND"), ("USA", "JPN"), ("USA", "DEU"),
    ("CHN", "IND"), ("CHN", "JPN"), ("CHN", "KOR"),
    ("IND", "PAK"), ("IND", "BGD"), ("IND", "IDN"), ("IND", "BRA"),
    # Europe
    ("DEU", "FRA"), ("DEU", "GBR"), ("GBR", "FRA"), ("ITA", "ESP"),
    ("POL", "CZE"), ("SWE", "NOR"), ("NLD", "BEL"),
    # Americas
    ("BRA", "MEX"), ("BRA", "ARG"), ("ARG", "CHL"), ("COL", "PER"),
    ("CAN", "AUS"), ("MEX", "COL"),
    # Asia
    ("JPN", "KOR"), ("THA", "VNM"), ("MYS", "SGP"), ("IDN", "PHL"),
    ("TWN", "KOR"), ("HKG", "SGP"),
    # Middle East
    ("SAU", "ARE"), ("TUR", "IRN"), ("ISR", "TUR"), ("QAT", "KWT"),
    # Africa
    ("ZAF", "NGA"), ("EGY", "MAR"), ("KEN", "ETH"), ("GHA", "CIV"),
    # Cross-regional
    ("RUS", "BRA"), ("TUR", "MEX"), ("ZAF", "IND"), ("AUS", "CAN"),
]


class TrainingDataBuilder:
    """Builds training dataset for the financial LLM."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the training data builder.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed or config.seed
        random.seed(self.seed)
        self.generator = DataGenerator(seed=self.seed)
        self.samples: List[Dict[str, str]] = []
    
    def _format_single_response(self, data: MacroeconomicDataPoint) -> str:
        """Format response for single country indicator query."""
        
        # Format values based on indicator type
        if data.indicator_code == "gdp_per_capita":
            fred_fmt = f"${data.fred_value:,.0f}"
            wb_fmt = f"${data.worldbank_value:,.0f}"
            oecd_fmt = f"${data.oecd_value:,.0f}"
            consensus_fmt = f"${data.consensus_value:,.0f}"
        elif data.indicator_code == "consumer_confidence":
            fred_fmt = f"{data.fred_value:.1f}"
            wb_fmt = f"{data.worldbank_value:.1f}"
            oecd_fmt = f"{data.oecd_value:.1f}"
            consensus_fmt = f"{data.consensus_value:.1f}"
        else:
            fred_fmt = f"{data.fred_value:.2f}%"
            wb_fmt = f"{data.worldbank_value:.2f}%"
            oecd_fmt = f"{data.oecd_value:.2f}%"
            consensus_fmt = f"{data.consensus_value:.2f}%"
        
        response = f"""Analysis of {data.indicator_name} for {data.country_name}

Country Profile:
- Region: {data.region}
- Sub-region: {data.sub_region}
- Income Level: {data.income_level.replace("_", " ").title()}

Data from Multiple Sources:
- FRED: {fred_fmt}
- World Bank: {wb_fmt}
- OECD: {oecd_fmt}
- Consensus Value: {consensus_fmt}

Confidence Assessment: {data.confidence_level}
{data.confidence_description}

{data.indicator_name} Assessment: {data.assessment_label}
{data.assessment_description}

Analysis:
{data.country_name}'s {data.indicator_name.lower()} of {consensus_fmt} reflects {data.assessment_description.lower()} This positions the country within the {data.region} regional context, considering its {data.income_level.replace("_", " ")} income classification.

Data Period: {data.period}
Sources: Federal Reserve Economic Data (FRED), World Bank Development Indicators, OECD Statistics"""

        return response
    
    def _format_comparison_response(
        self, 
        data1: MacroeconomicDataPoint, 
        data2: MacroeconomicDataPoint
    ) -> str:
        """Format response for country comparison query."""
        
        diff = data1.consensus_value - data2.consensus_value
        higher = data1.country_name if diff > 0 else data2.country_name
        lower = data2.country_name if diff > 0 else data1.country_name
        
        # Format values
        if data1.indicator_code == "gdp_per_capita":
            v1_fmt = f"${data1.consensus_value:,.0f}"
            v2_fmt = f"${data2.consensus_value:,.0f}"
            diff_fmt = f"${abs(diff):,.0f}"
        elif data1.indicator_code == "consumer_confidence":
            v1_fmt = f"{data1.consensus_value:.1f}"
            v2_fmt = f"{data2.consensus_value:.1f}"
            diff_fmt = f"{abs(diff):.1f} points"
        else:
            v1_fmt = f"{data1.consensus_value:.2f}%"
            v2_fmt = f"{data2.consensus_value:.2f}%"
            diff_fmt = f"{abs(diff):.2f} percentage points"
        
        response = f"""{data1.indicator_name} Comparison: {data1.country_name} vs {data2.country_name}

Country Profiles:
| Attribute | {data1.country_name} | {data2.country_name} |
|-----------|----------------------|----------------------|
| Region | {data1.region} | {data2.region} |
| Sub-region | {data1.sub_region} | {data2.sub_region} |
| Income Level | {data1.income_level.replace("_", " ").title()} | {data2.income_level.replace("_", " ").title()} |

Data Comparison:
| Source | {data1.country_name} | {data2.country_name} |
|--------|----------------------|----------------------|
| FRED | {data1.fred_value:.2f} | {data2.fred_value:.2f} |
| World Bank | {data1.worldbank_value:.2f} | {data2.worldbank_value:.2f} |
| OECD | {data1.oecd_value:.2f} | {data2.oecd_value:.2f} |
| Consensus | {v1_fmt} | {v2_fmt} |

Assessment:
- {data1.country_name}: {data1.assessment_label} - {data1.assessment_description}
- {data2.country_name}: {data2.assessment_label} - {data2.assessment_description}

Key Finding:
{higher} has higher {data1.indicator_name.lower()} by {diff_fmt} compared to {lower}.

Confidence: High (multi-source verification for both countries)
Data Period: {data1.period}
Sources: FRED, World Bank, OECD"""

        return response
    
    def _format_regional_response(
        self, 
        region: str,
        indicator_code: str,
        data_points: List[MacroeconomicDataPoint]
    ) -> str:
        """Format response for regional analysis query."""
        
        if not data_points:
            return f"No data available for {region}."
        
        indicator = INDICATORS[indicator_code]
        
        # Calculate statistics
        values = [d.consensus_value for d in data_points]
        avg_value = sum(values) / len(values)
        max_data = max(data_points, key=lambda x: x.consensus_value)
        min_data = min(data_points, key=lambda x: x.consensus_value)
        
        # Format values
        if indicator_code == "gdp_per_capita":
            avg_fmt = f"${avg_value:,.0f}"
            max_fmt = f"${max_data.consensus_value:,.0f}"
            min_fmt = f"${min_data.consensus_value:,.0f}"
        elif indicator_code == "consumer_confidence":
            avg_fmt = f"{avg_value:.1f}"
            max_fmt = f"{max_data.consensus_value:.1f}"
            min_fmt = f"{min_data.consensus_value:.1f}"
        else:
            avg_fmt = f"{avg_value:.2f}%"
            max_fmt = f"{max_data.consensus_value:.2f}%"
            min_fmt = f"{min_data.consensus_value:.2f}%"
        
        # Build country breakdown
        country_lines = []
        for i, data in enumerate(data_points[:10], 1):
            if indicator_code == "gdp_per_capita":
                val_fmt = f"${data.consensus_value:,.0f}"
            elif indicator_code == "consumer_confidence":
                val_fmt = f"{data.consensus_value:.1f}"
            else:
                val_fmt = f"{data.consensus_value:.2f}%"
            country_lines.append(f"{i}. {data.country_name}: {val_fmt} ({data.assessment_label})")
        
        response = f"""Regional Analysis: {indicator.display_name} in {region}

Summary Statistics:
- Regional Average: {avg_fmt}
- Highest: {max_fmt} ({max_data.country_name})
- Lowest: {min_fmt} ({min_data.country_name})
- Countries Analyzed: {len(data_points)}

Country Breakdown:
{chr(10).join(country_lines)}

Regional Assessment:
The {region} region shows {"significant" if (max_data.consensus_value - min_data.consensus_value) > avg_value * 0.5 else "moderate"} variation in {indicator.display_name.lower()} across member countries. This reflects differences in economic development, policy frameworks, and structural factors within the region.

Data Sources: FRED, World Bank, OECD
Confidence: High (multi-source triangulation)
Data Period: 2024"""

        return response
    
    def _format_ranking_response(
        self, 
        indicator_code: str,
        data_points: List[MacroeconomicDataPoint],
        top_n: int = 10
    ) -> str:
        """Format response for global ranking query."""
        
        indicator = INDICATORS[indicator_code]
        top_data = data_points[:top_n]
        
        # Build ranking lines
        ranking_lines = []
        for i, data in enumerate(top_data, 1):
            if indicator_code == "gdp_per_capita":
                val_fmt = f"${data.consensus_value:,.0f}"
            elif indicator_code == "consumer_confidence":
                val_fmt = f"{data.consensus_value:.1f}"
            else:
                val_fmt = f"{data.consensus_value:.2f}%"
            ranking_lines.append(f"{i}. {data.country_name} ({data.region}): {val_fmt}")
        
        higher_is_better = indicator.higher_is_better
        criteria = "Highest" if higher_is_better else "Lowest"
        
        response = f"""Global Ranking: Top {top_n} Countries by {indicator.display_name}

Ranking Criteria: {criteria} values

{chr(10).join(ranking_lines)}

Methodology:
Rankings based on consensus values derived from triangulated data from FRED, World Bank, and OECD. All values verified through multi-source analysis for accuracy and reliability.

Data Period: 2024
Confidence: High
Sources: FRED, World Bank, OECD"""

        return response
    
    def generate_single_indicator_samples(self) -> int:
        """Generate samples for single country indicator queries."""
        count = 0
        
        for country_code, country_info in COUNTRIES.items():
            if country_code == "EUU":
                continue
            
            for indicator_code in INDICATORS.keys():
                data = self.generator.generate_data_point(country_code, indicator_code)
                if not data:
                    continue
                
                templates = QUESTION_TEMPLATES.get(indicator_code, [])
                selected = random.sample(
                    templates, 
                    min(config.samples_per_country_indicator, len(templates))
                )
                
                response = self._format_single_response(data)
                
                for template in selected:
                    question = template.format(country_info.name)
                    self.samples.append({
                        "instruction": SYSTEM_INSTRUCTION,
                        "input": question,
                        "output": response
                    })
                    count += 1
        
        return count
    
    def generate_comparison_samples(self) -> int:
        """Generate samples for country comparison queries."""
        if not config.include_comparisons:
            return 0
        
        count = 0
        pairs = COMPARISON_PAIRS[:config.max_comparison_pairs]
        
        for code1, code2 in pairs:
            if code1 not in COUNTRIES or code2 not in COUNTRIES:
                continue
            
            # Select subset of indicators
            indicators = random.sample(list(INDICATORS.keys()), 6)
            
            for indicator_code in indicators:
                data1 = self.generator.generate_data_point(code1, indicator_code)
                data2 = self.generator.generate_data_point(code2, indicator_code)
                
                if not data1 or not data2:
                    continue
                
                country1_name = COUNTRIES[code1].name
                country2_name = COUNTRIES[code2].name
                indicator_name = INDICATORS[indicator_code].display_name.lower()
                
                questions = [
                    f"Compare {country1_name} and {country2_name} {indicator_name}.",
                    f"How does {country1_name}'s {indicator_name} compare to {country2_name}?",
                ]
                
                response = self._format_comparison_response(data1, data2)
                
                for question in questions:
                    self.samples.append({
                        "instruction": SYSTEM_INSTRUCTION,
                        "input": question,
                        "output": response
                    })
                    count += 1
        
        return count
    
    def generate_regional_samples(self) -> int:
        """Generate samples for regional analysis queries."""
        if not config.include_regional_analysis:
            return 0
        
        count = 0
        
        for region in REGIONS.keys():
            # Select subset of indicators
            indicators = random.sample(list(INDICATORS.keys()), 4)
            
            for indicator_code in indicators:
                data_points = self.generator.generate_region_data(region, indicator_code)
                
                if len(data_points) < 3:
                    continue
                
                # Sort by value
                indicator = INDICATORS[indicator_code]
                reverse = indicator.higher_is_better if indicator.higher_is_better is not None else True
                data_points.sort(key=lambda x: x.consensus_value, reverse=reverse)
                
                indicator_name = indicator.display_name.lower()
                
                questions = [
                    f"What is the {indicator_name} situation across {region}?",
                    f"Compare {indicator_name} in {region} countries.",
                    f"Analyze {indicator_name} trends in {region}.",
                ]
                
                response = self._format_regional_response(region, indicator_code, data_points)
                
                for question in questions[:2]:
                    self.samples.append({
                        "instruction": SYSTEM_INSTRUCTION,
                        "input": question,
                        "output": response
                    })
                    count += 1
        
        return count
    
    def generate_ranking_samples(self) -> int:
        """Generate samples for global ranking queries."""
        if not config.include_rankings:
            return 0
        
        count = 0
        
        for indicator_code in INDICATORS.keys():
            data_points = self.generator.generate_global_data(indicator_code)
            
            if len(data_points) < 10:
                continue
            
            indicator_name = INDICATORS[indicator_code].display_name.lower()
            
            questions = [
                f"Which countries have the highest {indicator_name}?",
                f"What are the top 10 countries by {indicator_name}?",
                f"Rank countries by {indicator_name}.",
                f"Show me the global {indicator_name} rankings.",
            ]
            
            response = self._format_ranking_response(indicator_code, data_points, 10)
            
            for question in questions[:2]:
                self.samples.append({
                    "instruction": SYSTEM_INSTRUCTION,
                    "input": question,
                    "output": response
                })
                count += 1
        
        return count
    
    def build(self) -> List[Dict[str, str]]:
        """
        Build complete training dataset.
        
        Returns:
            List of training samples
        """
        self.samples = []
        
        # Generate different types of samples
        single_count = self.generate_single_indicator_samples()
        comparison_count = self.generate_comparison_samples()
        regional_count = self.generate_regional_samples()
        ranking_count = self.generate_ranking_samples()
        
        # Shuffle samples
        random.shuffle(self.samples)
        
        return self.samples
    
    def save(
        self, 
        output_path: Optional[Path] = None,
        validation_split: Optional[float] = None
    ) -> Tuple[Path, Optional[Path]]:
        """
        Save training data to file.
        
        Args:
            output_path: Path to save training data
            validation_split: Fraction of data for validation
            
        Returns:
            Tuple of (training_path, validation_path)
        """
        if not self.samples:
            self.build()
        
        output_path = output_path or config.training_data_path
        validation_split = validation_split or config.validation_split
        
        # Split data
        if validation_split > 0:
            split_idx = int(len(self.samples) * (1 - validation_split))
            train_samples = self.samples[:split_idx]
            val_samples = self.samples[split_idx:]
            
            # Save training data
            with open(output_path, 'w', encoding='utf-8') as f:
                for sample in train_samples:
                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')
training_data_builder            
            # Save validation data
            val_path = config.validation_data_path
            with open(val_path, 'w', encoding='utf-8') as f:
                for sample in val_samples:
                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')
            
            return output_path, val_path
        else:
            # Save all data as training
            with open(output_path, 'w', encoding='utf-8') as f:
                for sample in self.samples:
                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')
            
            return output_path, None
    
    def get_statistics(self) -> Dict:
        """Get statistics about the generated dataset."""
        return {
            "total_samples": len(self.samples),
            "countries": len([c for c in COUNTRIES.keys() if c != "EUU"]),
            "indicators": len(INDICATORS),
            "regions": len(REGIONS),
        }