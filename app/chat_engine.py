"""
Chat Engine
===========
Orchestrates chat interactions with data integration.
"""

import logging
import re
import time
from typing import Dict, List, Optional, Tuple, Any

from model_loader import model_loader
from config import model_config
from data_fetcher import data_fetcher, get_data, get_many, TriangulatedData
from countries import COUNTRIES, REGIONS
from indicators import INDICATORS

logger = logging.getLogger(__name__)


# Country name aliases for intent detection
COUNTRY_ALIASES: Dict[str, str] = {
    "usa": "USA", "us": "USA", "america": "USA", "united states": "USA",
    "uk": "GBR", "britain": "GBR", "england": "GBR", "united kingdom": "GBR",
    "china": "CHN", "prc": "CHN",
    "india": "IND",
    "japan": "JPN",
    "germany": "DEU",
    "france": "FRA",
    "brazil": "BRA",
    "russia": "RUS",
    "south korea": "KOR", "korea": "KOR",
    "australia": "AUS",
    "canada": "CAN",
    "mexico": "MEX",
    "indonesia": "IDN",
    "saudi": "SAU", "saudi arabia": "SAU",
    "turkey": "TUR", "turkiye": "TUR",
    "south africa": "ZAF",
    "nigeria": "NGA",
    "egypt": "EGY",
    "eu": "EUU", "european union": "EUU", "europe": "EUU",
    "uae": "ARE", "emirates": "ARE",
    "vietnam": "VNM",
    "thailand": "THA",
    "malaysia": "MYS",
    "singapore": "SGP",
    "philippines": "PHL",
    "pakistan": "PAK",
    "bangladesh": "BGD",
    "sri lanka": "LKA",
    "nepal": "NPL",
    "argentina": "ARG",
    "chile": "CHL",
    "colombia": "COL",
    "peru": "PER",
    "venezuela": "VEN",
    "poland": "POL",
    "czech": "CZE", "czech republic": "CZE",
    "hungary": "HUN",
    "romania": "ROU",
    "ukraine": "UKR",
    "sweden": "SWE",
    "norway": "NOR",
    "denmark": "DNK",
    "finland": "FIN",
    "netherlands": "NLD", "holland": "NLD",
    "belgium": "BEL",
    "switzerland": "CHE",
    "austria": "AUT",
    "ireland": "IRL",
    "italy": "ITA",
    "spain": "ESP",
    "portugal": "PRT",
    "greece": "GRC",
    "israel": "ISR",
    "iran": "IRN",
    "iraq": "IRQ",
    "qatar": "QAT",
    "kuwait": "KWT",
    "morocco": "MAR",
    "algeria": "DZA",
    "kenya": "KEN",
    "ethiopia": "ETH",
    "ghana": "GHA",
    "tanzania": "TZA",
    "new zealand": "NZL",
}

# Metric keywords for intent detection
METRIC_KEYWORDS: Dict[str, List[str]] = {
    "gdp_growth": ["gdp", "growth", "economic growth", "economy growing", "gdp growth"],
    "inflation": ["inflation", "cpi", "prices", "price level", "cost of living", "inflationary"],
    "unemployment": ["unemployment", "jobless", "jobs", "labor", "employment", "job market", "unemployed"],
    "interest_rate": ["interest rate", "rates", "monetary policy", "central bank", "fed", "ecb", "rbi", "policy rate", "benchmark rate"],
    "gdp_per_capita": ["gdp per capita", "income level", "per capita", "wealth per person", "income per person"],
    "current_account": ["current account", "external balance", "balance of payments", "external position"],
    "government_debt": ["debt", "government debt", "public debt", "fiscal debt", "debt to gdp", "national debt"],
    "fdi_inflows": ["fdi", "foreign direct investment", "foreign investment", "investment inflows"],
    "exchange_rate_change": ["exchange rate", "currency", "forex", "fx", "currency movement", "appreciation", "depreciation"],
    "industrial_production": ["industrial production", "manufacturing", "industrial output", "factory output", "industry"],
    "consumer_confidence": ["consumer confidence", "consumer sentiment", "household sentiment", "consumer outlook"],
    "trade_balance": ["trade balance", "trade surplus", "trade deficit", "exports", "imports", "trade position"],
}


# Words that say which end of a ranking the user wants. Only consulted once a
# query has already been classified as a ranking, so adding a common word like
# "most" here cannot change which branch a query takes.
#
# "highest"/"lowest" order by raw value; "best"/"worst" order by the indicator's
# higher_is_better. They differ for anything where a bigger number is worse --
# "highest unemployment" and "best unemployment" are opposite ends of the list.
RANKING_DIRECTION_WORDS: List[Tuple[str, str]] = [
    ("highest", "highest"), ("top", "highest"), ("most", "highest"),
    ("largest", "highest"), ("greatest", "highest"), ("biggest", "highest"),
    ("leading", "highest"), ("max", "highest"), ("maximum", "highest"),
    ("lowest", "lowest"), ("least", "lowest"), ("smallest", "lowest"),
    ("bottom", "lowest"), ("fewest", "lowest"), ("min", "lowest"),
    ("minimum", "lowest"),
    ("best", "best"),
    ("worst", "worst"),
]


# How each direction reads in the prompt, so the model captions the list the
# way it was actually sorted.
RANKING_ORDER_NOTES: Dict[Optional[str], str] = {
    "highest": "highest value first",
    "lowest": "lowest value first",
    "best": "best performer first",
    "worst": "worst performer first",
    None: "best performer first",
}


def detect_ranking_direction(query_lower: str) -> Optional[str]:
    """
    Return "highest" / "lowest" / "best" / "worst", or None if unstated.

    The earliest word in the sentence wins, so "highest unemployment, worst
    first" resolves to the phrasing the user led with. Matching is on word
    boundaries -- otherwise "most" fires on "almost" and "top" on "stop".
    """
    best_pos = None
    best_direction = None
    for word, direction in RANKING_DIRECTION_WORDS:
        match = re.search(rf"\b{word}\b", query_lower)
        if match and (best_pos is None or match.start() < best_pos):
            best_pos = match.start()
            best_direction = direction
    return best_direction


class ChatEngine:
    """Orchestrates chat interactions with live data integration."""
    
    def __init__(self):
        """Initialize the chat engine."""
        self.conversation_history: List[Dict] = []
    
    def detect_intent(self, query: str) -> Dict:
        """
        Detect user intent from the query.
        
        Args:
            query: User's input query
            
        Returns:
            Dictionary with detected intent information
        """
        query_lower = query.lower()
        
        intent = {
            "type": "general",
            "countries": [],
            "indicators": [],
            "is_comparison": False,
            "is_ranking": False,
            "ranking_direction": None,
            "is_regional": False,
            "region": None,
        }
        
        # Detect indicators
        for indicator_code, keywords in METRIC_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                intent["indicators"].append(indicator_code)
        
        # Default to GDP growth if no indicator detected
        if not intent["indicators"]:
            intent["indicators"] = ["gdp_growth"]
        
        # Detect countries by name
        for code, country_info in COUNTRIES.items():
            if country_info.name.lower() in query_lower:
                if code not in intent["countries"]:
                    intent["countries"].append(code)
        
        # Detect countries by alias
        for alias, code in COUNTRY_ALIASES.items():
            if alias in query_lower and code not in intent["countries"]:
                intent["countries"].append(code)
        
        # Detect comparison intent
        comparison_words = ["compare", "vs", "versus", "difference", "between", "comparison"]
        intent["is_comparison"] = any(w in query_lower for w in comparison_words)
        
        # Detect ranking intent
        ranking_words = ["ranking", "top", "highest", "lowest", "best", "worst", "rank", "leading"]
        intent["is_ranking"] = any(w in query_lower for w in ranking_words)
        if intent["is_ranking"]:
            intent["ranking_direction"] = detect_ranking_direction(query_lower)
        
        # Detect regional intent
        for region in REGIONS.keys():
            region_lower = region.lower()
            if region_lower in query_lower or region_lower.replace(" - ", " ") in query_lower:
                intent["is_regional"] = True
                intent["region"] = region
                break
        
        # Determine query type
        if intent["is_comparison"] and len(intent["countries"]) >= 2:
            intent["type"] = "comparison"
        elif intent["is_ranking"]:
            intent["type"] = "ranking"
        elif intent["is_regional"] and intent["region"]:
            intent["type"] = "regional"
        elif intent["countries"]:
            intent["type"] = "single_country"
        else:
            intent["type"] = "general"
        
        return intent
    
    def fetch_relevant_data(self, intent: Dict, use_live: bool = True) -> List[TriangulatedData]:
        """
        Fetch data based on detected intent.
        
        Args:
            intent: Detected intent dictionary
            use_live: Whether to fetch from live APIs or use modelled values
            
        Returns:
            List of TriangulatedData objects
        """
        data = []
        
        if intent["type"] == "ranking":
            # Get global or regional ranking, ordered the way the user asked
            direction = intent.get("ranking_direction")
            for indicator in intent["indicators"][:1]:  # Limit to first indicator
                if intent["is_regional"] and intent["region"]:
                    ranking_data = data_fetcher.get_region_data(
                        indicator, intent["region"], live=use_live,
                        direction=direction
                    )
                else:
                    ranking_data = data_fetcher.get_global_ranking(
                        indicator, limit=10, live=use_live, direction=direction
                    )
                data.extend(ranking_data)
        
        elif intent["type"] == "regional":
            # Get regional data
            for indicator in intent["indicators"][:2]:  # Limit to 2 indicators
                regional_data = data_fetcher.get_region_data(
                    indicator, intent["region"], live=use_live
                )
                data.extend(regional_data[:10])
        
        elif intent["type"] == "comparison":
            # Get comparison data - use bulk fetch
            for indicator in intent["indicators"][:2]:  # Limit to 2 indicators
                comparison_data = get_many(
                    indicator, intent["countries"][:3], live=use_live
                )
                data.extend(comparison_data)
        
        elif intent["type"] == "single_country":
            # Get single country data
            for country in intent["countries"][:1]:  # Limit to first country
                for indicator in intent["indicators"][:3]:  # Limit to 3 indicators
                    country_data = get_data(indicator, country, live=use_live)
                    if country_data.consensus_value is not None:
                        data.append(country_data)
        
        return data
    
    def format_data_context(
        self,
        data: List[TriangulatedData],
        intent: Optional[Dict] = None
    ) -> str:
        """
        Format fetched data as context for the model (compressed for speed).
        """
        if not data:
            return ""
        
        lines = ["### DATA CONTEXT:"]
        
        # Detect whether the batch is live or modelled so the model knows.
        live_count = sum(1 for d in data if d.is_live)
        if live_count > 0:
            lines.append(f"Data mode: LIVE from upstream APIs ({live_count}/{len(data)} resolved live)")
        else:
            lines.append("Data mode: MODELLED (regional baseline)")
        
        # State the sort order explicitly. Without this the model narrates
        # whatever ranking criteria it saw most often in training, which is how
        # a "highest unemployment" list came back captioned "Lowest values".
        if intent and intent.get("is_ranking"):
            lines.append(
                f"Rows are already sorted {RANKING_ORDER_NOTES[intent.get('ranking_direction')]}. "
                "List them in the order given."
            )
        
        for d in data:
            # Format value based on indicator type
            if d.indicator_code == "gdp_per_capita":
                val = f"${d.consensus_value:,.0f}"
            elif d.indicator_code == "consumer_confidence":
                val = f"{d.consensus_value:.1f}"
            else:
                val = f"{d.consensus_value:.2f}%"
            
            # Dense single-line format to save tokens and speed up TTFT
            context_line = (
                f"- {d.country_name} ({d.region}) | {d.indicator_name}: {val} | "
                f"Conf: {d.confidence_level} | Assess: {d.assessment_label} | "
                f"Period: {d.period} | Source: {d.source_note}"
            )
            lines.append(context_line)
        
        return "\n".join(lines)
    
    def build_model_input(
        self,
        user_query: str,
        data: List[TriangulatedData],
        intent: Optional[Dict] = None
    ) -> Tuple[str, List[TriangulatedData]]:
        """
        Assemble what gets sent to the model, trimming data rows until the
        answer has room to finish.

        A ten-row ranking builds a ~600-token prompt, which inside a 768-token
        window leaves too little for a complete reply -- the model stops
        mid-word with nothing to signal it. Dropping the tail rows is what
        actually buys a whole answer; clamping max_tokens alone only makes the
        truncation tidier.

        Returns the prompt input and the rows that survived, so callers can
        show exactly what the model saw.
        """
        def build(rows: List[TriangulatedData]) -> str:
            context = self.format_data_context(rows, intent) if rows else ""
            if not context:
                return user_query
            return f"{user_query}\n\n{context}"

        enhanced_query = build(data)
        if not data:
            return enhanced_query, data

        kept = len(data)
        while (
            kept > 1
            and model_loader.answer_budget(enhanced_query)
            < model_config.min_answer_tokens
        ):
            kept -= 1
            enhanced_query = build(data[:kept])

        if kept < len(data):
            logger.info(
                f"PROFILING: trimmed data context {len(data)} -> {kept} rows "
                f"to leave {model_config.min_answer_tokens}+ tokens for the answer"
            )
            data = data[:kept]

        return enhanced_query, data

    def generate_response(
        self,
        user_query: str,
        use_live_data: bool = True
    ):
        """
        Generate a response to the user's query (streaming).
        
        Args:
            user_query: The user's input query
            use_live_data: Whether to fetch and include live API data
            
        Yields:
            Chunks of text, and finally a list of TriangulatedData
        """
        # Detect intent
        intent = self.detect_intent(user_query)
        
        # Fetch relevant data
        data = []
        if use_live_data:
            start_fetch = time.time()
            data = self.fetch_relevant_data(intent, use_live=use_live_data)
            fetch_duration = time.time() - start_fetch
            logger.info(f"PROFILING: Data fetch took {fetch_duration:.2f}s")
        
        enhanced_query, data = self.build_model_input(user_query, data, intent)

        # Generate response from model
        full_response = ""
        try:
            start_gen = time.time()
            first_token_time = None
            
            for chunk in model_loader.generate_stream(enhanced_query):
                if first_token_time is None:
                    first_token_time = time.time()
                    logger.info(f"PROFILING: Time to first token: {first_token_time - start_gen:.2f}s")
                
                full_response += chunk
                yield chunk, None
            
            gen_duration = time.time() - start_gen
            logger.info(f"PROFILING: Total generation took {gen_duration:.2f}s")

            # Trimming makes this rare, but a verbose answer can still run out
            # the clamped budget. Say so rather than ending mid-sentence.
            if model_loader.last_finish_reason == "length":
                notice = (
                    "\n\n_(Response cut short at the model's context limit. "
                    "Ask about fewer countries or one indicator for a full answer.)_"
                )
                full_response += notice
                yield notice, None
        except Exception as e:
            logger.error(f"Model generation error: {e}")
            error_msg = f"I apologize, but I encountered an error generating a response: {str(e)}"
            yield error_msg, None
            full_response = error_msg
        
        # Add to conversation history
        self.conversation_history.append({
            "query": user_query,
            "intent": intent,
            "response": full_response,
            "data": data,
        })
        
        # Limit history size
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
        
        # Final yield of data
        yield "", data
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_suggested_questions(self, country_code: Optional[str] = None) -> List[str]:
        """
        Get suggested questions based on context.
        
        Args:
            country_code: Optional country code for context
            
        Returns:
            List of suggested question strings
        """
        if country_code and country_code in COUNTRIES:
            country_name = COUNTRIES[country_code].name
            return [
                f"What is the GDP growth rate for {country_name}?",
                f"What is the inflation rate in {country_name}?",
                f"What is the unemployment situation in {country_name}?",
                f"Compare {country_name}'s economy to regional peers.",
            ]
        
        return [
            "What is India's GDP growth rate?",
            "Compare USA and China inflation.",
            "Which countries have the highest unemployment?",
            "What is the economic outlook for Europe?",
            "Tell me about Brazil's current account balance.",
            "What is Japan's government debt level?",
            "How is Vietnam's industrial production performing?",
            "Compare Germany and France GDP per capita.",
        ]


# Global instance
chat_engine = ChatEngine()