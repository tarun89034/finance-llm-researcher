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
    currency_name: str
    fred_code: Optional[str] = None
    worldbank_code: Optional[str] = None
    oecd_code: Optional[str] = None
    is_oecd_member: bool = False


# Comprehensive country database
COUNTRIES: Dict[str, CountryInfo] = {
    
    # =========================================================================
    # NORTH AMERICA
    # =========================================================================
    "USA": CountryInfo(
        code="USA",
        name="United States",
        region="North America",
        sub_region="Northern America",
        income_level="high",
        currency="USD",
        currency_name="US Dollar",
        fred_code="US",
        worldbank_code="USA",
        oecd_code="USA",
        is_oecd_member=True
    ),
    "CAN": CountryInfo(
        code="CAN",
        name="Canada",
        region="North America",
        sub_region="Northern America",
        income_level="high",
        currency="CAD",
        currency_name="Canadian Dollar",
        fred_code="CA",
        worldbank_code="CAN",
        oecd_code="CAN",
        is_oecd_member=True
    ),
    "MEX": CountryInfo(
        code="MEX",
        name="Mexico",
        region="North America",
        sub_region="Central America",
        income_level="upper_middle",
        currency="MXN",
        currency_name="Mexican Peso",
        fred_code="MX",
        worldbank_code="MEX",
        oecd_code="MEX",
        is_oecd_member=True
    ),
    
    # =========================================================================
    # SOUTH AMERICA
    # =========================================================================
    "BRA": CountryInfo(
        code="BRA",
        name="Brazil",
        region="South America",
        sub_region="South America",
        income_level="upper_middle",
        currency="BRL",
        currency_name="Brazilian Real",
        fred_code="BR",
        worldbank_code="BRA",
        oecd_code=None,
        is_oecd_member=False
    ),
    "ARG": CountryInfo(
        code="ARG",
        name="Argentina",
        region="South America",
        sub_region="South America",
        income_level="upper_middle",
        currency="ARS",
        currency_name="Argentine Peso",
        fred_code="AR",
        worldbank_code="ARG",
        oecd_code=None,
        is_oecd_member=False
    ),
    "CHL": CountryInfo(
        code="CHL",
        name="Chile",
        region="South America",
        sub_region="South America",
        income_level="high",
        currency="CLP",
        currency_name="Chilean Peso",
        fred_code="CL",
        worldbank_code="CHL",
        oecd_code="CHL",
        is_oecd_member=True
    ),
    "COL": CountryInfo(
        code="COL",
        name="Colombia",
        region="South America",
        sub_region="South America",
        income_level="upper_middle",
        currency="COP",
        currency_name="Colombian Peso",
        fred_code="CO",
        worldbank_code="COL",
        oecd_code="COL",
        is_oecd_member=True
    ),
    "PER": CountryInfo(
        code="PER",
        name="Peru",
        region="South America",
        sub_region="South America",
        income_level="upper_middle",
        currency="PEN",
        currency_name="Peruvian Sol",
        fred_code="PE",
        worldbank_code="PER",
        oecd_code=None,
        is_oecd_member=False
    ),
    "VEN": CountryInfo(
        code="VEN",
        name="Venezuela",
        region="South America",
        sub_region="South America",
        income_level="upper_middle",
        currency="VES",
        currency_name="Venezuelan Bolivar",
        fred_code="VE",
        worldbank_code="VEN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "ECU": CountryInfo(
        code="ECU",
        name="Ecuador",
        region="South America",
        sub_region="South America",
        income_level="upper_middle",
        currency="USD",
        currency_name="US Dollar",
        fred_code=None,
        worldbank_code="ECU",
        oecd_code=None,
        is_oecd_member=False
    ),
    "BOL": CountryInfo(
        code="BOL",
        name="Bolivia",
        region="South America",
        sub_region="South America",
        income_level="lower_middle",
        currency="BOB",
        currency_name="Bolivian Boliviano",
        fred_code=None,
        worldbank_code="BOL",
        oecd_code=None,
        is_oecd_member=False
    ),
    "URY": CountryInfo(
        code="URY",
        name="Uruguay",
        region="South America",
        sub_region="South America",
        income_level="high",
        currency="UYU",
        currency_name="Uruguayan Peso",
        fred_code=None,
        worldbank_code="URY",
        oecd_code=None,
        is_oecd_member=False
    ),
    "PRY": CountryInfo(
        code="PRY",
        name="Paraguay",
        region="South America",
        sub_region="South America",
        income_level="upper_middle",
        currency="PYG",
        currency_name="Paraguayan Guarani",
        fred_code=None,
        worldbank_code="PRY",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # EUROPE - WESTERN
    # =========================================================================
    "GBR": CountryInfo(
        code="GBR",
        name="United Kingdom",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="GBP",
        currency_name="British Pound",
        fred_code="UK",
        worldbank_code="GBR",
        oecd_code="GBR",
        is_oecd_member=True
    ),
    "DEU": CountryInfo(
        code="DEU",
        name="Germany",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="DE",
        worldbank_code="DEU",
        oecd_code="DEU",
        is_oecd_member=True
    ),
    "FRA": CountryInfo(
        code="FRA",
        name="France",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="FR",
        worldbank_code="FRA",
        oecd_code="FRA",
        is_oecd_member=True
    ),
    "NLD": CountryInfo(
        code="NLD",
        name="Netherlands",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="NL",
        worldbank_code="NLD",
        oecd_code="NLD",
        is_oecd_member=True
    ),
    "BEL": CountryInfo(
        code="BEL",
        name="Belgium",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="BE",
        worldbank_code="BEL",
        oecd_code="BEL",
        is_oecd_member=True
    ),
    "CHE": CountryInfo(
        code="CHE",
        name="Switzerland",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="CHF",
        currency_name="Swiss Franc",
        fred_code="CH",
        worldbank_code="CHE",
        oecd_code="CHE",
        is_oecd_member=True
    ),
    "AUT": CountryInfo(
        code="AUT",
        name="Austria",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="AT",
        worldbank_code="AUT",
        oecd_code="AUT",
        is_oecd_member=True
    ),
    "IRL": CountryInfo(
        code="IRL",
        name="Ireland",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="IE",
        worldbank_code="IRL",
        oecd_code="IRL",
        is_oecd_member=True
    ),
    "LUX": CountryInfo(
        code="LUX",
        name="Luxembourg",
        region="Europe",
        sub_region="Western Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code=None,
        worldbank_code="LUX",
        oecd_code="LUX",
        is_oecd_member=True
    ),
    
    # =========================================================================
    # EUROPE - NORTHERN
    # =========================================================================
    "SWE": CountryInfo(
        code="SWE",
        name="Sweden",
        region="Europe",
        sub_region="Northern Europe",
        income_level="high",
        currency="SEK",
        currency_name="Swedish Krona",
        fred_code="SE",
        worldbank_code="SWE",
        oecd_code="SWE",
        is_oecd_member=True
    ),
    "NOR": CountryInfo(
        code="NOR",
        name="Norway",
        region="Europe",
        sub_region="Northern Europe",
        income_level="high",
        currency="NOK",
        currency_name="Norwegian Krone",
        fred_code="NO",
        worldbank_code="NOR",
        oecd_code="NOR",
        is_oecd_member=True
    ),
    "DNK": CountryInfo(
        code="DNK",
        name="Denmark",
        region="Europe",
        sub_region="Northern Europe",
        income_level="high",
        currency="DKK",
        currency_name="Danish Krone",
        fred_code="DK",
        worldbank_code="DNK",
        oecd_code="DNK",
        is_oecd_member=True
    ),
    "FIN": CountryInfo(
        code="FIN",
        name="Finland",
        region="Europe",
        sub_region="Northern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="FI",
        worldbank_code="FIN",
        oecd_code="FIN",
        is_oecd_member=True
    ),
    "ISL": CountryInfo(
        code="ISL",
        name="Iceland",
        region="Europe",
        sub_region="Northern Europe",
        income_level="high",
        currency="ISK",
        currency_name="Icelandic Krona",
        fred_code=None,
        worldbank_code="ISL",
        oecd_code="ISL",
        is_oecd_member=True
    ),
    
    # =========================================================================
    # EUROPE - SOUTHERN
    # =========================================================================
    "ITA": CountryInfo(
        code="ITA",
        name="Italy",
        region="Europe",
        sub_region="Southern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="IT",
        worldbank_code="ITA",
        oecd_code="ITA",
        is_oecd_member=True
    ),
    "ESP": CountryInfo(
        code="ESP",
        name="Spain",
        region="Europe",
        sub_region="Southern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="ES",
        worldbank_code="ESP",
        oecd_code="ESP",
        is_oecd_member=True
    ),
    "PRT": CountryInfo(
        code="PRT",
        name="Portugal",
        region="Europe",
        sub_region="Southern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="PT",
        worldbank_code="PRT",
        oecd_code="PRT",
        is_oecd_member=True
    ),
    "GRC": CountryInfo(
        code="GRC",
        name="Greece",
        region="Europe",
        sub_region="Southern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="GR",
        worldbank_code="GRC",
        oecd_code="GRC",
        is_oecd_member=True
    ),
    "SVN": CountryInfo(
        code="SVN",
        name="Slovenia",
        region="Europe",
        sub_region="Southern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="SI",
        worldbank_code="SVN",
        oecd_code="SVN",
        is_oecd_member=True
    ),
    "HRV": CountryInfo(
        code="HRV",
        name="Croatia",
        region="Europe",
        sub_region="Southern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="HR",
        worldbank_code="HRV",
        oecd_code=None,
        is_oecd_member=False
    ),
    "SRB": CountryInfo(
        code="SRB",
        name="Serbia",
        region="Europe",
        sub_region="Southern Europe",
        income_level="upper_middle",
        currency="RSD",
        currency_name="Serbian Dinar",
        fred_code=None,
        worldbank_code="SRB",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # EUROPE - EASTERN
    # =========================================================================
    "POL": CountryInfo(
        code="POL",
        name="Poland",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="high",
        currency="PLN",
        currency_name="Polish Zloty",
        fred_code="PL",
        worldbank_code="POL",
        oecd_code="POL",
        is_oecd_member=True
    ),
    "CZE": CountryInfo(
        code="CZE",
        name="Czech Republic",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="high",
        currency="CZK",
        currency_name="Czech Koruna",
        fred_code="CZ",
        worldbank_code="CZE",
        oecd_code="CZE",
        is_oecd_member=True
    ),
    "HUN": CountryInfo(
        code="HUN",
        name="Hungary",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="high",
        currency="HUF",
        currency_name="Hungarian Forint",
        fred_code="HU",
        worldbank_code="HUN",
        oecd_code="HUN",
        is_oecd_member=True
    ),
    "ROU": CountryInfo(
        code="ROU",
        name="Romania",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="upper_middle",
        currency="RON",
        currency_name="Romanian Leu",
        fred_code="RO",
        worldbank_code="ROU",
        oecd_code=None,
        is_oecd_member=False
    ),
    "BGR": CountryInfo(
        code="BGR",
        name="Bulgaria",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="upper_middle",
        currency="BGN",
        currency_name="Bulgarian Lev",
        fred_code="BG",
        worldbank_code="BGR",
        oecd_code=None,
        is_oecd_member=False
    ),
    "UKR": CountryInfo(
        code="UKR",
        name="Ukraine",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="lower_middle",
        currency="UAH",
        currency_name="Ukrainian Hryvnia",
        fred_code="UA",
        worldbank_code="UKR",
        oecd_code=None,
        is_oecd_member=False
    ),
    "SVK": CountryInfo(
        code="SVK",
        name="Slovakia",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="SK",
        worldbank_code="SVK",
        oecd_code="SVK",
        is_oecd_member=True
    ),
    "EST": CountryInfo(
        code="EST",
        name="Estonia",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code=None,
        worldbank_code="EST",
        oecd_code="EST",
        is_oecd_member=True
    ),
    "LVA": CountryInfo(
        code="LVA",
        name="Latvia",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code=None,
        worldbank_code="LVA",
        oecd_code="LVA",
        is_oecd_member=True
    ),
    "LTU": CountryInfo(
        code="LTU",
        name="Lithuania",
        region="Europe",
        sub_region="Eastern Europe",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code=None,
        worldbank_code="LTU",
        oecd_code="LTU",
        is_oecd_member=True
    ),
    
    # =========================================================================
    # RUSSIA AND CIS
    # =========================================================================
    "RUS": CountryInfo(
        code="RUS",
        name="Russia",
        region="Russia and CIS",
        sub_region="Eastern Europe",
        income_level="upper_middle",
        currency="RUB",
        currency_name="Russian Ruble",
        fred_code="RU",
        worldbank_code="RUS",
        oecd_code=None,
        is_oecd_member=False
    ),
    "KAZ": CountryInfo(
        code="KAZ",
        name="Kazakhstan",
        region="Russia and CIS",
        sub_region="Central Asia",
        income_level="upper_middle",
        currency="KZT",
        currency_name="Kazakhstani Tenge",
        fred_code=None,
        worldbank_code="KAZ",
        oecd_code=None,
        is_oecd_member=False
    ),
    "UZB": CountryInfo(
        code="UZB",
        name="Uzbekistan",
        region="Russia and CIS",
        sub_region="Central Asia",
        income_level="lower_middle",
        currency="UZS",
        currency_name="Uzbekistani Som",
        fred_code=None,
        worldbank_code="UZB",
        oecd_code=None,
        is_oecd_member=False
    ),
    "BLR": CountryInfo(
        code="BLR",
        name="Belarus",
        region="Russia and CIS",
        sub_region="Eastern Europe",
        income_level="upper_middle",
        currency="BYN",
        currency_name="Belarusian Ruble",
        fred_code=None,
        worldbank_code="BLR",
        oecd_code=None,
        is_oecd_member=False
    ),
    "AZE": CountryInfo(
        code="AZE",
        name="Azerbaijan",
        region="Russia and CIS",
        sub_region="Western Asia",
        income_level="upper_middle",
        currency="AZN",
        currency_name="Azerbaijani Manat",
        fred_code=None,
        worldbank_code="AZE",
        oecd_code=None,
        is_oecd_member=False
    ),
    "GEO": CountryInfo(
        code="GEO",
        name="Georgia",
        region="Russia and CIS",
        sub_region="Western Asia",
        income_level="upper_middle",
        currency="GEL",
        currency_name="Georgian Lari",
        fred_code=None,
        worldbank_code="GEO",
        oecd_code=None,
        is_oecd_member=False
    ),
    "ARM": CountryInfo(
        code="ARM",
        name="Armenia",
        region="Russia and CIS",
        sub_region="Western Asia",
        income_level="upper_middle",
        currency="AMD",
        currency_name="Armenian Dram",
        fred_code=None,
        worldbank_code="ARM",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # ASIA - EAST
    # =========================================================================
    "CHN": CountryInfo(
        code="CHN",
        name="China",
        region="Asia",
        sub_region="Eastern Asia",
        income_level="upper_middle",
        currency="CNY",
        currency_name="Chinese Yuan",
        fred_code="CN",
        worldbank_code="CHN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "JPN": CountryInfo(
        code="JPN",
        name="Japan",
        region="Asia",
        sub_region="Eastern Asia",
        income_level="high",
        currency="JPY",
        currency_name="Japanese Yen",
        fred_code="JP",
        worldbank_code="JPN",
        oecd_code="JPN",
        is_oecd_member=True
    ),
    "KOR": CountryInfo(
        code="KOR",
        name="South Korea",
        region="Asia",
        sub_region="Eastern Asia",
        income_level="high",
        currency="KRW",
        currency_name="South Korean Won",
        fred_code="KR",
        worldbank_code="KOR",
        oecd_code="KOR",
        is_oecd_member=True
    ),
    "TWN": CountryInfo(
        code="TWN",
        name="Taiwan",
        region="Asia",
        sub_region="Eastern Asia",
        income_level="high",
        currency="TWD",
        currency_name="New Taiwan Dollar",
        fred_code="TW",
        worldbank_code="TWN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "HKG": CountryInfo(
        code="HKG",
        name="Hong Kong",
        region="Asia",
        sub_region="Eastern Asia",
        income_level="high",
        currency="HKD",
        currency_name="Hong Kong Dollar",
        fred_code="HK",
        worldbank_code="HKG",
        oecd_code=None,
        is_oecd_member=False
    ),
    "MNG": CountryInfo(
        code="MNG",
        name="Mongolia",
        region="Asia",
        sub_region="Eastern Asia",
        income_level="lower_middle",
        currency="MNT",
        currency_name="Mongolian Tugrik",
        fred_code=None,
        worldbank_code="MNG",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # ASIA - SOUTH
    # =========================================================================
    "IND": CountryInfo(
        code="IND",
        name="India",
        region="Asia",
        sub_region="Southern Asia",
        income_level="lower_middle",
        currency="INR",
        currency_name="Indian Rupee",
        fred_code="IN",
        worldbank_code="IND",
        oecd_code=None,
        is_oecd_member=False
    ),
    "PAK": CountryInfo(
        code="PAK",
        name="Pakistan",
        region="Asia",
        sub_region="Southern Asia",
        income_level="lower_middle",
        currency="PKR",
        currency_name="Pakistani Rupee",
        fred_code="PK",
        worldbank_code="PAK",
        oecd_code=None,
        is_oecd_member=False
    ),
    "BGD": CountryInfo(
        code="BGD",
        name="Bangladesh",
        region="Asia",
        sub_region="Southern Asia",
        income_level="lower_middle",
        currency="BDT",
        currency_name="Bangladeshi Taka",
        fred_code="BD",
        worldbank_code="BGD",
        oecd_code=None,
        is_oecd_member=False
    ),
    "LKA": CountryInfo(
        code="LKA",
        name="Sri Lanka",
        region="Asia",
        sub_region="Southern Asia",
        income_level="lower_middle",
        currency="LKR",
        currency_name="Sri Lankan Rupee",
        fred_code=None,
        worldbank_code="LKA",
        oecd_code=None,
        is_oecd_member=False
    ),
    "NPL": CountryInfo(
        code="NPL",
        name="Nepal",
        region="Asia",
        sub_region="Southern Asia",
        income_level="lower_middle",
        currency="NPR",
        currency_name="Nepalese Rupee",
        fred_code=None,
        worldbank_code="NPL",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # ASIA - SOUTHEAST
    # =========================================================================
    "IDN": CountryInfo(
        code="IDN",
        name="Indonesia",
        region="Asia",
        sub_region="South-Eastern Asia",
        income_level="upper_middle",
        currency="IDR",
        currency_name="Indonesian Rupiah",
        fred_code="ID",
        worldbank_code="IDN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "THA": CountryInfo(
        code="THA",
        name="Thailand",
        region="Asia",
        sub_region="South-Eastern Asia",
        income_level="upper_middle",
        currency="THB",
        currency_name="Thai Baht",
        fred_code="TH",
        worldbank_code="THA",
        oecd_code=None,
        is_oecd_member=False
    ),
    "VNM": CountryInfo(
        code="VNM",
        name="Vietnam",
        region="Asia",
        sub_region="South-Eastern Asia",
        income_level="lower_middle",
        currency="VND",
        currency_name="Vietnamese Dong",
        fred_code="VN",
        worldbank_code="VNM",
        oecd_code=None,
        is_oecd_member=False
    ),
    "MYS": CountryInfo(
        code="MYS",
        name="Malaysia",
        region="Asia",
        sub_region="South-Eastern Asia",
        income_level="upper_middle",
        currency="MYR",
        currency_name="Malaysian Ringgit",
        fred_code="MY",
        worldbank_code="MYS",
        oecd_code=None,
        is_oecd_member=False
    ),
    "SGP": CountryInfo(
        code="SGP",
        name="Singapore",
        region="Asia",
        sub_region="South-Eastern Asia",
        income_level="high",
        currency="SGD",
        currency_name="Singapore Dollar",
        fred_code="SG",
        worldbank_code="SGP",
        oecd_code=None,
        is_oecd_member=False
    ),
    "PHL": CountryInfo(
        code="PHL",
        name="Philippines",
        region="Asia",
        sub_region="South-Eastern Asia",
        income_level="lower_middle",
        currency="PHP",
        currency_name="Philippine Peso",
        fred_code="PH",
        worldbank_code="PHL",
        oecd_code=None,
        is_oecd_member=False
    ),
    "MMR": CountryInfo(
        code="MMR",
        name="Myanmar",
        region="Asia",
        sub_region="South-Eastern Asia",
        income_level="lower_middle",
        currency="MMK",
        currency_name="Myanmar Kyat",
        fred_code=None,
        worldbank_code="MMR",
        oecd_code=None,
        is_oecd_member=False
    ),
    "KHM": CountryInfo(
        code="KHM",
        name="Cambodia",
        region="Asia",
        sub_region="South-Eastern Asia",
        income_level="lower_middle",
        currency="KHR",
        currency_name="Cambodian Riel",
        fred_code=None,
        worldbank_code="KHM",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # MIDDLE EAST
    # =========================================================================
    "SAU": CountryInfo(
        code="SAU",
        name="Saudi Arabia",
        region="Middle East",
        sub_region="Western Asia",
        income_level="high",
        currency="SAR",
        currency_name="Saudi Riyal",
        fred_code="SA",
        worldbank_code="SAU",
        oecd_code=None,
        is_oecd_member=False
    ),
    "ARE": CountryInfo(
        code="ARE",
        name="United Arab Emirates",
        region="Middle East",
        sub_region="Western Asia",
        income_level="high",
        currency="AED",
        currency_name="UAE Dirham",
        fred_code="AE",
        worldbank_code="ARE",
        oecd_code=None,
        is_oecd_member=False
    ),
    "ISR": CountryInfo(
        code="ISR",
        name="Israel",
        region="Middle East",
        sub_region="Western Asia",
        income_level="high",
        currency="ILS",
        currency_name="Israeli Shekel",
        fred_code="IL",
        worldbank_code="ISR",
        oecd_code="ISR",
        is_oecd_member=True
    ),
    "TUR": CountryInfo(
        code="TUR",
        name="Turkey",
        region="Middle East",
        sub_region="Western Asia",
        income_level="upper_middle",
        currency="TRY",
        currency_name="Turkish Lira",
        fred_code="TR",
        worldbank_code="TUR",
        oecd_code="TUR",
        is_oecd_member=True
    ),
    "IRN": CountryInfo(
        code="IRN",
        name="Iran",
        region="Middle East",
        sub_region="Western Asia",
        income_level="lower_middle",
        currency="IRR",
        currency_name="Iranian Rial",
        fred_code="IR",
        worldbank_code="IRN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "IRQ": CountryInfo(
        code="IRQ",
        name="Iraq",
        region="Middle East",
        sub_region="Western Asia",
        income_level="upper_middle",
        currency="IQD",
        currency_name="Iraqi Dinar",
        fred_code=None,
        worldbank_code="IRQ",
        oecd_code=None,
        is_oecd_member=False
    ),
    "QAT": CountryInfo(
        code="QAT",
        name="Qatar",
        region="Middle East",
        sub_region="Western Asia",
        income_level="high",
        currency="QAR",
        currency_name="Qatari Riyal",
        fred_code="QA",
        worldbank_code="QAT",
        oecd_code=None,
        is_oecd_member=False
    ),
    "KWT": CountryInfo(
        code="KWT",
        name="Kuwait",
        region="Middle East",
        sub_region="Western Asia",
        income_level="high",
        currency="KWD",
        currency_name="Kuwaiti Dinar",
        fred_code="KW",
        worldbank_code="KWT",
        oecd_code=None,
        is_oecd_member=False
    ),
    "OMN": CountryInfo(
        code="OMN",
        name="Oman",
        region="Middle East",
        sub_region="Western Asia",
        income_level="high",
        currency="OMR",
        currency_name="Omani Rial",
        fred_code=None,
        worldbank_code="OMN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "JOR": CountryInfo(
        code="JOR",
        name="Jordan",
        region="Middle East",
        sub_region="Western Asia",
        income_level="upper_middle",
        currency="JOD",
        currency_name="Jordanian Dinar",
        fred_code=None,
        worldbank_code="JOR",
        oecd_code=None,
        is_oecd_member=False
    ),
    "LBN": CountryInfo(
        code="LBN",
        name="Lebanon",
        region="Middle East",
        sub_region="Western Asia",
        income_level="upper_middle",
        currency="LBP",
        currency_name="Lebanese Pound",
        fred_code=None,
        worldbank_code="LBN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "BHR": CountryInfo(
        code="BHR",
        name="Bahrain",
        region="Middle East",
        sub_region="Western Asia",
        income_level="high",
        currency="BHD",
        currency_name="Bahraini Dinar",
        fred_code=None,
        worldbank_code="BHR",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # AFRICA - NORTH
    # =========================================================================
    "EGY": CountryInfo(
        code="EGY",
        name="Egypt",
        region="Africa",
        sub_region="Northern Africa",
        income_level="lower_middle",
        currency="EGP",
        currency_name="Egyptian Pound",
        fred_code="EG",
        worldbank_code="EGY",
        oecd_code=None,
        is_oecd_member=False
    ),
    "MAR": CountryInfo(
        code="MAR",
        name="Morocco",
        region="Africa",
        sub_region="Northern Africa",
        income_level="lower_middle",
        currency="MAD",
        currency_name="Moroccan Dirham",
        fred_code="MA",
        worldbank_code="MAR",
        oecd_code=None,
        is_oecd_member=False
    ),
    "DZA": CountryInfo(
        code="DZA",
        name="Algeria",
        region="Africa",
        sub_region="Northern Africa",
        income_level="lower_middle",
        currency="DZD",
        currency_name="Algerian Dinar",
        fred_code=None,
        worldbank_code="DZA",
        oecd_code=None,
        is_oecd_member=False
    ),
    "TUN": CountryInfo(
        code="TUN",
        name="Tunisia",
        region="Africa",
        sub_region="Northern Africa",
        income_level="lower_middle",
        currency="TND",
        currency_name="Tunisian Dinar",
        fred_code=None,
        worldbank_code="TUN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "LBY": CountryInfo(
        code="LBY",
        name="Libya",
        region="Africa",
        sub_region="Northern Africa",
        income_level="upper_middle",
        currency="LYD",
        currency_name="Libyan Dinar",
        fred_code=None,
        worldbank_code="LBY",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # AFRICA - SUB-SAHARAN
    # =========================================================================
    "ZAF": CountryInfo(
        code="ZAF",
        name="South Africa",
        region="Africa",
        sub_region="Southern Africa",
        income_level="upper_middle",
        currency="ZAR",
        currency_name="South African Rand",
        fred_code="ZA",
        worldbank_code="ZAF",
        oecd_code=None,
        is_oecd_member=False
    ),
    "NGA": CountryInfo(
        code="NGA",
        name="Nigeria",
        region="Africa",
        sub_region="Western Africa",
        income_level="lower_middle",
        currency="NGN",
        currency_name="Nigerian Naira",
        fred_code="NG",
        worldbank_code="NGA",
        oecd_code=None,
        is_oecd_member=False
    ),
    "KEN": CountryInfo(
        code="KEN",
        name="Kenya",
        region="Africa",
        sub_region="Eastern Africa",
        income_level="lower_middle",
        currency="KES",
        currency_name="Kenyan Shilling",
        fred_code="KE",
        worldbank_code="KEN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "ETH": CountryInfo(
        code="ETH",
        name="Ethiopia",
        region="Africa",
        sub_region="Eastern Africa",
        income_level="low",
        currency="ETB",
        currency_name="Ethiopian Birr",
        fred_code=None,
        worldbank_code="ETH",
        oecd_code=None,
        is_oecd_member=False
    ),
    "GHA": CountryInfo(
        code="GHA",
        name="Ghana",
        region="Africa",
        sub_region="Western Africa",
        income_level="lower_middle",
        currency="GHS",
        currency_name="Ghanaian Cedi",
        fred_code=None,
        worldbank_code="GHA",
        oecd_code=None,
        is_oecd_member=False
    ),
    "TZA": CountryInfo(
        code="TZA",
        name="Tanzania",
        region="Africa",
        sub_region="Eastern Africa",
        income_level="lower_middle",
        currency="TZS",
        currency_name="Tanzanian Shilling",
        fred_code=None,
        worldbank_code="TZA",
        oecd_code=None,
        is_oecd_member=False
    ),
    "UGA": CountryInfo(
        code="UGA",
        name="Uganda",
        region="Africa",
        sub_region="Eastern Africa",
        income_level="low",
        currency="UGX",
        currency_name="Ugandan Shilling",
        fred_code=None,
        worldbank_code="UGA",
        oecd_code=None,
        is_oecd_member=False
    ),
    "AGO": CountryInfo(
        code="AGO",
        name="Angola",
        region="Africa",
        sub_region="Middle Africa",
        income_level="lower_middle",
        currency="AOA",
        currency_name="Angolan Kwanza",
        fred_code=None,
        worldbank_code="AGO",
        oecd_code=None,
        is_oecd_member=False
    ),
    "SEN": CountryInfo(
        code="SEN",
        name="Senegal",
        region="Africa",
        sub_region="Western Africa",
        income_level="lower_middle",
        currency="XOF",
        currency_name="CFA Franc",
        fred_code=None,
        worldbank_code="SEN",
        oecd_code=None,
        is_oecd_member=False
    ),
    "CIV": CountryInfo(
        code="CIV",
        name="Ivory Coast",
        region="Africa",
        sub_region="Western Africa",
        income_level="lower_middle",
        currency="XOF",
        currency_name="CFA Franc",
        fred_code=None,
        worldbank_code="CIV",
        oecd_code=None,
        is_oecd_member=False
    ),
    "CMR": CountryInfo(
        code="CMR",
        name="Cameroon",
        region="Africa",
        sub_region="Middle Africa",
        income_level="lower_middle",
        currency="XAF",
        currency_name="CFA Franc",
        fred_code=None,
        worldbank_code="CMR",
        oecd_code=None,
        is_oecd_member=False
    ),
    "ZWE": CountryInfo(
        code="ZWE",
        name="Zimbabwe",
        region="Africa",
        sub_region="Eastern Africa",
        income_level="lower_middle",
        currency="ZWL",
        currency_name="Zimbabwean Dollar",
        fred_code=None,
        worldbank_code="ZWE",
        oecd_code=None,
        is_oecd_member=False
    ),
    "RWA": CountryInfo(
        code="RWA",
        name="Rwanda",
        region="Africa",
        sub_region="Eastern Africa",
        income_level="low",
        currency="RWF",
        currency_name="Rwandan Franc",
        fred_code=None,
        worldbank_code="RWA",
        oecd_code=None,
        is_oecd_member=False
    ),
    
    # =========================================================================
    # OCEANIA
    # =========================================================================
    "AUS": CountryInfo(
        code="AUS",
        name="Australia",
        region="Oceania",
        sub_region="Australia and New Zealand",
        income_level="high",
        currency="AUD",
        currency_name="Australian Dollar",
        fred_code="AU",
        worldbank_code="AUS",
        oecd_code="AUS",
        is_oecd_member=True
    ),
    "NZL": CountryInfo(
        code="NZL",
        name="New Zealand",
        region="Oceania",
        sub_region="Australia and New Zealand",
        income_level="high",
        currency="NZD",
        currency_name="New Zealand Dollar",
        fred_code="NZ",
        worldbank_code="NZL",
        oecd_code="NZL",
        is_oecd_member=True
    ),
    
    # =========================================================================
    # AGGREGATES
    # =========================================================================
    "EUU": CountryInfo(
        code="EUU",
        name="European Union",
        region="Aggregates",
        sub_region="European Union",
        income_level="high",
        currency="EUR",
        currency_name="Euro",
        fred_code="EU",
        worldbank_code="EUU",
        oecd_code="EA19",
        is_oecd_member=True
    ),
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


def get_countries_by_region(region: str) -> Dict[str, CountryInfo]:
    """Get all countries in a specific region."""
    codes = REGIONS.get(region, [])
    return {code: COUNTRIES[code] for code in codes if code in COUNTRIES}


def get_countries_by_income(income_level: str) -> Dict[str, CountryInfo]:
    """Get all countries with a specific income level."""
    return {
        code: info for code, info in COUNTRIES.items()
        if info.income_level == income_level
    }


def get_oecd_members() -> Dict[str, CountryInfo]:
    """Get all OECD member countries."""
    return {
        code: info for code, info in COUNTRIES.items()
        if info.is_oecd_member
    }


def get_country_count() -> int:
    """Get total number of countries (excluding aggregates)."""
    return len([c for c in COUNTRIES.keys() if c != "EUU"])


def search_country(query: str) -> List[CountryInfo]:
    """Search for countries by name."""
    query_lower = query.lower()
    results = []
    for info in COUNTRIES.values():
        if query_lower in info.name.lower():
            results.append(info)
    return results