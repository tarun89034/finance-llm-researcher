"""
Direct World Bank API test to diagnose the issue.
"""

import sys
sys.path.insert(0, "app")

import requests
from datetime import datetime
from config import api_config

print("=" * 80)
print("WORLD BANK API DIRECT TEST")
print("=" * 80)

# Test parameters
country = "DEU"  # Germany
indicator = "FP.CPI.TOTL.ZG"  # Inflation
current_year = datetime.now().year
date_range = f"{current_year - 6}:{current_year}"

url = f"{api_config.worldbank_base_url}/country/{country}/indicator/{indicator}"

print(f"\nRequest:")
print(f"  URL: {url}")
print(f"  Params:")
print(f"    format: json")
print(f"    per_page: 50")
print(f"    date: {date_range}")

try:
    response = requests.get(
        url,
        params={
            "format": "json",
            "per_page": 50,
            "date": date_range,
        },
        timeout=12,
    )
    
    print(f"\nResponse:")
    print(f"  Status: {response.status_code}")
    print(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Payload type: {type(data)}")
        print(f"  Payload length: {len(data) if isinstance(data, list) else 'N/A'}")
        
        if isinstance(data, list) and len(data) >= 2:
            metadata = data[0]
            observations = data[1]
            print(f"\nMetadata:")
            print(f"  Page: {metadata.get('page')}")
            print(f"  Pages: {metadata.get('pages')}")
            print(f"  Per page: {metadata.get('per_page')}")
            print(f"  Total: {metadata.get('total')}")
            
            print(f"\nObservations:")
            if observations:
                print(f"  Count: {len(observations)}")
                print(f"  Sample (first 5):")
                for obs in observations[:5]:
                    country_name = obs.get("country", {}).get("value", "Unknown")
                    year = obs.get("date", "N/A")
                    value = obs.get("value")
                    print(f"    {year}: {value} ({country_name})")
            else:
                print(f"  Count: 0 (no observations returned)")
        else:
            print(f"\nUnexpected payload structure:")
            print(f"  {data}")
    else:
        print(f"  Error: {response.status_code}")
        print(f"  Body: {response.text[:500]}")
        
except Exception as e:
    print(f"\nException: {e}")

print(f"\n{'=' * 80}")
