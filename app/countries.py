"""
Country Database
================
Comprehensive database of 80+ countries with regional classifications.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CountryInfo:
    """Information about a single country."""
    code: str
    name: str
    region: str
    sub_region: str
    income_level: str
    currency: str
    flag_emoji: str


# =============================================================================
# LIVE DATA SOURCE CODE MAPPINGS
# =============================================================================
# FRED builds series IDs from two-letter country codes rather than ISO-3, so
# indicator templates such as "LMUNRRTT{country}M156S" need this lookup.
# Countries absent from this map have no FRED coverage in this project.
FRED_COUNTRY_CODES: Dict[str, str] = {
    "USA": "US", "CAN": "CA", "MEX": "MX",
    "BRA": "BR", "ARG": "AR", "CHL": "CL", "COL": "CO", "PER": "PE", "VEN": "VE",
    "GBR": "UK", "DEU": "DE", "FRA": "FR", "NLD": "NL", "BEL": "BE", "CHE": "CH",
    "AUT": "AT", "IRL": "IE",
    "SWE": "SE", "NOR": "NO", "DNK": "DK", "FIN": "FI",
    "ITA": "IT", "ESP": "ES", "PRT": "PT", "GRC": "GR", "SVN": "SI", "HRV": "HR",
    "POL": "PL", "CZE": "CZ", "HUN": "HU", "ROU": "RO", "BGR": "BG", "UKR": "UA",
    "SVK": "SK", "RUS": "RU",
    "CHN": "CN", "JPN": "JP", "KOR": "KR", "TWN": "TW", "HKG": "HK",
    "IND": "IN", "PAK": "PK", "BGD": "BD",
    "IDN": "ID", "THA": "TH", "VNM": "VN", "MYS": "MY", "SGP": "SG", "PHL": "PH",
    "SAU": "SA", "ARE": "AE", "ISR": "IL", "TUR": "TR", "IRN": "IR", "QAT": "QA",
    "KWT": "KW",
    "EGY": "EG", "MAR": "MA", "ZAF": "ZA", "NGA": "NG", "KEN": "KE",
    "AUS": "AU", "NZL": "NZ",
    "EUU": "EU",
}

# OECD member states. Reserved for the OECD SDMX client, which is not wired up.
OECD_MEMBERS: frozenset = frozenset({
    "AUS", "AUT", "BEL", "CAN", "CHE", "CHL", "COL", "CZE", "DEU", "DNK", "ESP",
    "EST", "EUU", "FIN", "FRA", "GBR", "GRC", "HUN", "IRL", "ISL", "ISR", "ITA",
    "JPN", "KOR", "LTU", "LUX", "LVA", "MEX", "NLD", "NOR", "NZL", "POL", "PRT",
    "SVK", "SVN", "SWE", "TUR", "USA",
})


def get_fred_code(country_code: str) -> Optional[str]:
    """Return the FRED two-letter code for a country, or None if unsupported."""
    return FRED_COUNTRY_CODES.get(country_code)


def get_worldbank_code(country_code: str) -> str:
    """Return the World Bank country code (the ISO-3 code is used directly)."""
    return country_code


def is_oecd_member(country_code: str) -> bool:
    """Return True when the country is an OECD member."""
    return country_code in OECD_MEMBERS


# Comprehensive country database
COUNTRIES: Dict[str, CountryInfo] = {
    # North America
    "USA": CountryInfo("USA", "United States", "North America", "Northern America", "high", "USD", "🇺🇸"),
    "CAN": CountryInfo("CAN", "Canada", "North America", "Northern America", "high", "CAD", "🇨🇦"),
    "MEX": CountryInfo("MEX", "Mexico", "North America", "Central America", "upper_middle", "MXN", "🇲🇽"),
    
    # South America
    "BRA": CountryInfo("BRA", "Brazil", "South America", "South America", "upper_middle", "BRL", "🇧🇷"),
    "ARG": CountryInfo("ARG", "Argentina", "South America", "South America", "upper_middle", "ARS", "🇦🇷"),
    "CHL": CountryInfo("CHL", "Chile", "South America", "South America", "high", "CLP", "🇨🇱"),
    "COL": CountryInfo("COL", "Colombia", "South America", "South America", "upper_middle", "COP", "🇨🇴"),
    "PER": CountryInfo("PER", "Peru", "South America", "South America", "upper_middle", "PEN", "🇵🇪"),
    "VEN": CountryInfo("VEN", "Venezuela", "South America", "South America", "upper_middle", "VES", "🇻🇪"),
    "ECU": CountryInfo("ECU", "Ecuador", "South America", "South America", "upper_middle", "USD", "🇪🇨"),
    "BOL": CountryInfo("BOL", "Bolivia", "South America", "South America", "lower_middle", "BOB", "🇧🇴"),
    "URY": CountryInfo("URY", "Uruguay", "South America", "South America", "high", "UYU", "🇺🇾"),
    "PRY": CountryInfo("PRY", "Paraguay", "South America", "South America", "upper_middle", "PYG", "🇵🇾"),
    
    # Europe - Western
    "GBR": CountryInfo("GBR", "United Kingdom", "Europe", "Western Europe", "high", "GBP", "🇬🇧"),
    "DEU": CountryInfo("DEU", "Germany", "Europe", "Western Europe", "high", "EUR", "🇩🇪"),
    "FRA": CountryInfo("FRA", "France", "Europe", "Western Europe", "high", "EUR", "🇫🇷"),
    "NLD": CountryInfo("NLD", "Netherlands", "Europe", "Western Europe", "high", "EUR", "🇳🇱"),
    "BEL": CountryInfo("BEL", "Belgium", "Europe", "Western Europe", "high", "EUR", "🇧🇪"),
    "CHE": CountryInfo("CHE", "Switzerland", "Europe", "Western Europe", "high", "CHF", "🇨🇭"),
    "AUT": CountryInfo("AUT", "Austria", "Europe", "Western Europe", "high", "EUR", "🇦🇹"),
    "IRL": CountryInfo("IRL", "Ireland", "Europe", "Western Europe", "high", "EUR", "🇮🇪"),
    "LUX": CountryInfo("LUX", "Luxembourg", "Europe", "Western Europe", "high", "EUR", "🇱🇺"),
    
    # Europe - Northern
    "SWE": CountryInfo("SWE", "Sweden", "Europe", "Northern Europe", "high", "SEK", "🇸🇪"),
    "NOR": CountryInfo("NOR", "Norway", "Europe", "Northern Europe", "high", "NOK", "🇳🇴"),
    "DNK": CountryInfo("DNK", "Denmark", "Europe", "Northern Europe", "high", "DKK", "🇩🇰"),
    "FIN": CountryInfo("FIN", "Finland", "Europe", "Northern Europe", "high", "EUR", "🇫🇮"),
    "ISL": CountryInfo("ISL", "Iceland", "Europe", "Northern Europe", "high", "ISK", "🇮🇸"),
    
    # Europe - Southern
    "ITA": CountryInfo("ITA", "Italy", "Europe", "Southern Europe", "high", "EUR", "🇮🇹"),
    "ESP": CountryInfo("ESP", "Spain", "Europe", "Southern Europe", "high", "EUR", "🇪🇸"),
    "PRT": CountryInfo("PRT", "Portugal", "Europe", "Southern Europe", "high", "EUR", "🇵🇹"),
    "GRC": CountryInfo("GRC", "Greece", "Europe", "Southern Europe", "high", "EUR", "🇬🇷"),
    "SVN": CountryInfo("SVN", "Slovenia", "Europe", "Southern Europe", "high", "EUR", "🇸🇮"),
    "HRV": CountryInfo("HRV", "Croatia", "Europe", "Southern Europe", "high", "EUR", "🇭🇷"),
    "SRB": CountryInfo("SRB", "Serbia", "Europe", "Southern Europe", "upper_middle", "RSD", "🇷🇸"),
    
    # Europe - Eastern
    "POL": CountryInfo("POL", "Poland", "Europe", "Eastern Europe", "high", "PLN", "🇵🇱"),
    "CZE": CountryInfo("CZE", "Czech Republic", "Europe", "Eastern Europe", "high", "CZK", "🇨🇿"),
    "HUN": CountryInfo("HUN", "Hungary", "Europe", "Eastern Europe", "high", "HUF", "🇭🇺"),
    "ROU": CountryInfo("ROU", "Romania", "Europe", "Eastern Europe", "upper_middle", "RON", "🇷🇴"),
    "BGR": CountryInfo("BGR", "Bulgaria", "Europe", "Eastern Europe", "upper_middle", "BGN", "🇧🇬"),
    "UKR": CountryInfo("UKR", "Ukraine", "Europe", "Eastern Europe", "lower_middle", "UAH", "🇺🇦"),
    "SVK": CountryInfo("SVK", "Slovakia", "Europe", "Eastern Europe", "high", "EUR", "🇸🇰"),
    "EST": CountryInfo("EST", "Estonia", "Europe", "Eastern Europe", "high", "EUR", "🇪🇪"),
    "LVA": CountryInfo("LVA", "Latvia", "Europe", "Eastern Europe", "high", "EUR", "🇱🇻"),
    "LTU": CountryInfo("LTU", "Lithuania", "Europe", "Eastern Europe", "high", "EUR", "🇱🇹"),
    
    # Russia and CIS
    "RUS": CountryInfo("RUS", "Russia", "Russia and CIS", "Eastern Europe", "upper_middle", "RUB", "🇷🇺"),
    "KAZ": CountryInfo("KAZ", "Kazakhstan", "Russia and CIS", "Central Asia", "upper_middle", "KZT", "🇰🇿"),
    "UZB": CountryInfo("UZB", "Uzbekistan", "Russia and CIS", "Central Asia", "lower_middle", "UZS", "🇺🇿"),
    "BLR": CountryInfo("BLR", "Belarus", "Russia and CIS", "Eastern Europe", "upper_middle", "BYN", "🇧🇾"),
    "AZE": CountryInfo("AZE", "Azerbaijan", "Russia and CIS", "Western Asia", "upper_middle", "AZN", "🇦🇿"),
    "GEO": CountryInfo("GEO", "Georgia", "Russia and CIS", "Western Asia", "upper_middle", "GEL", "🇬🇪"),
    "ARM": CountryInfo("ARM", "Armenia", "Russia and CIS", "Western Asia", "upper_middle", "AMD", "🇦🇲"),
    
    # Asia - East
    "CHN": CountryInfo("CHN", "China", "Asia", "Eastern Asia", "upper_middle", "CNY", "🇨🇳"),
    "JPN": CountryInfo("JPN", "Japan", "Asia", "Eastern Asia", "high", "JPY", "🇯🇵"),
    "KOR": CountryInfo("KOR", "South Korea", "Asia", "Eastern Asia", "high", "KRW", "🇰🇷"),
    "TWN": CountryInfo("TWN", "Taiwan", "Asia", "Eastern Asia", "high", "TWD", "🇹🇼"),
    "HKG": CountryInfo("HKG", "Hong Kong", "Asia", "Eastern Asia", "high", "HKD", "🇭🇰"),
    "MNG": CountryInfo("MNG", "Mongolia", "Asia", "Eastern Asia", "lower_middle", "MNT", "🇲🇳"),
    
    # Asia - South
    "IND": CountryInfo("IND", "India", "Asia", "Southern Asia", "lower_middle", "INR", "🇮🇳"),
    "PAK": CountryInfo("PAK", "Pakistan", "Asia", "Southern Asia", "lower_middle", "PKR", "🇵🇰"),
    "BGD": CountryInfo("BGD", "Bangladesh", "Asia", "Southern Asia", "lower_middle", "BDT", "🇧🇩"),
    "LKA": CountryInfo("LKA", "Sri Lanka", "Asia", "Southern Asia", "lower_middle", "LKR", "🇱🇰"),
    "NPL": CountryInfo("NPL", "Nepal", "Asia", "Southern Asia", "lower_middle", "NPR", "🇳🇵"),
    
    # Asia - Southeast
    "IDN": CountryInfo("IDN", "Indonesia", "Asia", "South-Eastern Asia", "upper_middle", "IDR", "🇮🇩"),
    "THA": CountryInfo("THA", "Thailand", "Asia", "South-Eastern Asia", "upper_middle", "THB", "🇹🇭"),
    "VNM": CountryInfo("VNM", "Vietnam", "Asia", "South-Eastern Asia", "lower_middle", "VND", "🇻🇳"),
    "MYS": CountryInfo("MYS", "Malaysia", "Asia", "South-Eastern Asia", "upper_middle", "MYR", "🇲🇾"),
    "SGP": CountryInfo("SGP", "Singapore", "Asia", "South-Eastern Asia", "high", "SGD", "🇸🇬"),
    "PHL": CountryInfo("PHL", "Philippines", "Asia", "South-Eastern Asia", "lower_middle", "PHP", "🇵🇭"),
    "MMR": CountryInfo("MMR", "Myanmar", "Asia", "South-Eastern Asia", "lower_middle", "MMK", "🇲🇲"),
    "KHM": CountryInfo("KHM", "Cambodia", "Asia", "South-Eastern Asia", "lower_middle", "KHR", "🇰🇭"),
    
    # Middle East
    "SAU": CountryInfo("SAU", "Saudi Arabia", "Middle East", "Western Asia", "high", "SAR", "🇸🇦"),
    "ARE": CountryInfo("ARE", "United Arab Emirates", "Middle East", "Western Asia", "high", "AED", "🇦🇪"),
    "ISR": CountryInfo("ISR", "Israel", "Middle East", "Western Asia", "high", "ILS", "🇮🇱"),
    "TUR": CountryInfo("TUR", "Turkey", "Middle East", "Western Asia", "upper_middle", "TRY", "🇹🇷"),
    "IRN": CountryInfo("IRN", "Iran", "Middle East", "Western Asia", "lower_middle", "IRR", "🇮🇷"),
    "IRQ": CountryInfo("IRQ", "Iraq", "Middle East", "Western Asia", "upper_middle", "IQD", "🇮🇶"),
    "QAT": CountryInfo("QAT", "Qatar", "Middle East", "Western Asia", "high", "QAR", "🇶🇦"),
    "KWT": CountryInfo("KWT", "Kuwait", "Middle East", "Western Asia", "high", "KWD", "🇰🇼"),
    "OMN": CountryInfo("OMN", "Oman", "Middle East", "Western Asia", "high", "OMR", "🇴🇲"),
    "JOR": CountryInfo("JOR", "Jordan", "Middle East", "Western Asia", "upper_middle", "JOD", "🇯🇴"),
    "LBN": CountryInfo("LBN", "Lebanon", "Middle East", "Western Asia", "upper_middle", "LBP", "🇱🇧"),
    "BHR": CountryInfo("BHR", "Bahrain", "Middle East", "Western Asia", "high", "BHD", "🇧🇭"),
    
    # Africa - North
    "EGY": CountryInfo("EGY", "Egypt", "Africa", "Northern Africa", "lower_middle", "EGP", "🇪🇬"),
    "MAR": CountryInfo("MAR", "Morocco", "Africa", "Northern Africa", "lower_middle", "MAD", "🇲🇦"),
    "DZA": CountryInfo("DZA", "Algeria", "Africa", "Northern Africa", "lower_middle", "DZD", "🇩🇿"),
    "TUN": CountryInfo("TUN", "Tunisia", "Africa", "Northern Africa", "lower_middle", "TND", "🇹🇳"),
    "LBY": CountryInfo("LBY", "Libya", "Africa", "Northern Africa", "upper_middle", "LYD", "🇱🇾"),
    
    # Africa - Sub-Saharan
    "ZAF": CountryInfo("ZAF", "South Africa", "Africa", "Southern Africa", "upper_middle", "ZAR", "🇿🇦"),
    "NGA": CountryInfo("NGA", "Nigeria", "Africa", "Western Africa", "lower_middle", "NGN", "🇳🇬"),
    "KEN": CountryInfo("KEN", "Kenya", "Africa", "Eastern Africa", "lower_middle", "KES", "🇰🇪"),
    "ETH": CountryInfo("ETH", "Ethiopia", "Africa", "Eastern Africa", "low", "ETB", "🇪🇹"),
    "GHA": CountryInfo("GHA", "Ghana", "Africa", "Western Africa", "lower_middle", "GHS", "🇬🇭"),
    "TZA": CountryInfo("TZA", "Tanzania", "Africa", "Eastern Africa", "lower_middle", "TZS", "🇹🇿"),
    "UGA": CountryInfo("UGA", "Uganda", "Africa", "Eastern Africa", "low", "UGX", "🇺🇬"),
    "AGO": CountryInfo("AGO", "Angola", "Africa", "Middle Africa", "lower_middle", "AOA", "🇦🇴"),
    "SEN": CountryInfo("SEN", "Senegal", "Africa", "Western Africa", "lower_middle", "XOF", "🇸🇳"),
    "CIV": CountryInfo("CIV", "Ivory Coast", "Africa", "Western Africa", "lower_middle", "XOF", "🇨🇮"),
    "CMR": CountryInfo("CMR", "Cameroon", "Africa", "Middle Africa", "lower_middle", "XAF", "🇨🇲"),
    "ZWE": CountryInfo("ZWE", "Zimbabwe", "Africa", "Eastern Africa", "lower_middle", "ZWL", "🇿🇼"),
    "RWA": CountryInfo("RWA", "Rwanda", "Africa", "Eastern Africa", "low", "RWF", "🇷🇼"),
    
    # Oceania
    "AUS": CountryInfo("AUS", "Australia", "Oceania", "Oceania", "high", "AUD", "🇦🇺"),
    "NZL": CountryInfo("NZL", "New Zealand", "Oceania", "Oceania", "high", "NZD", "🇳🇿"),
    
    # Aggregates
    "EUU": CountryInfo("EUU", "European Union", "Aggregates", "Europe", "high", "EUR", "🇪🇺"),
}


# Regional groupings
REGIONS: Dict[str, List[str]] = {
    "North America": ["USA", "CAN", "MEX"],
    "South America": ["BRA", "ARG", "CHL", "COL", "PER", "VEN", "ECU", "BOL", "URY", "PRY"],
    "Europe - Western": ["GBR", "DEU", "FRA", "NLD", "BEL", "CHE", "AUT", "IRL", "LUX"],
    "Europe - Northern": ["SWE", "NOR", "DNK", "FIN", "ISL"],
    "Europe - Southern": ["ITA", "ESP", "PRT", "GRC", "SVN", "HRV", "SRB"],
    "Europe - Eastern": ["POL", "CZE", "HUN", "ROU", "BGR", "UKR", "SVK", "EST", "LVA", "LTU"],
    "Russia and CIS": ["RUS", "KAZ", "UZB", "BLR", "AZE", "GEO", "ARM"],
    "Asia - East": ["CHN", "JPN", "KOR", "TWN", "HKG", "MNG"],
    "Asia - South": ["IND", "PAK", "BGD", "LKA", "NPL"],
    "Asia - Southeast": ["IDN", "THA", "VNM", "MYS", "SGP", "PHL", "MMR", "KHM"],
    "Middle East": ["SAU", "ARE", "ISR", "TUR", "IRN", "IRQ", "QAT", "KWT", "OMN", "JOR", "LBN", "BHR"],
    "Africa - North": ["EGY", "MAR", "DZA", "TUN", "LBY"],
    "Africa - Sub-Saharan": ["ZAF", "NGA", "KEN", "ETH", "GHA", "TZA", "UGA", "AGO", "SEN", "CIV", "CMR", "ZWE", "RWA"],
    "Oceania": ["AUS", "NZL"],
}


def get_country(code: str) -> Optional[CountryInfo]:
    """Get country info by code."""
    return COUNTRIES.get(code)


def get_countries_by_region(region: str) -> Dict[str, CountryInfo]:
    """Get all countries in a region."""
    codes = REGIONS.get(region, [])
    return {code: COUNTRIES[code] for code in codes if code in COUNTRIES}


def get_all_regions() -> List[str]:
    """Get all region names."""
    return list(REGIONS.keys())


def get_country_count() -> int:
    """Get total number of countries (excluding aggregates)."""
    return len([c for c in COUNTRIES.keys() if c != "EUU"])


def search_countries(query: str) -> List[CountryInfo]:
    """Search countries by name."""
    query_lower = query.lower()
    return [info for info in COUNTRIES.values() if query_lower in info.name.lower()]