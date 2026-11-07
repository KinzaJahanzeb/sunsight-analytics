# extract.py
"""Extract hourly weather data from NASA POWER API for all cities."""

import json
import time
from pathlib import Path

import requests

from config import (
    API_BASE,
    CITIES,
    END_YEAR,
    PARAMETERS,
    RAW_DIR,
    START_YEAR,
)


def fetch_city_data_chunk(city: str, lat: float, lon: float, year: int) -> dict:
    """Fetch raw JSON from NASA POWER for one city for ONE year."""
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": f"{year}0101",
        "end": f"{year}1231",
        "format": "JSON",
    }

    response = requests.get(API_BASE, params=params, timeout=120)
    
    if response.status_code != 200:
        print(f"\n[API ERROR {response.status_code} for {city} year {year}]: {response.text}")
        
    response.raise_for_status()
    return response.json()


def extract_all() -> None:
    """Fetch and cache raw JSON for every city, year by year."""
    Path(RAW_DIR).mkdir(parents=True, exist_ok=True)

    for city, coords in CITIES.items():
        raw_path = Path(RAW_DIR) / f"{city}.json"

        if raw_path.exists():
            print(f"[skip] {city} already cached")
            continue

        print(f"[fetch] {city} ...", end=" ", flush=True)
        
        # We must loop through 2020, 2021, 2022, 2023, 2024 to bypass NASA's JSON size limit
        combined_parameters = {}
        
        try:
            for year in range(START_YEAR, END_YEAR + 1):
                data = fetch_city_data_chunk(city, coords["lat"], coords["lon"], year)
                
                # Extract just the parameter data for this year
                year_params = data["properties"]["parameter"]
                
                # Merge into our main dictionary
                for param_name, values in year_params.items():
                    if param_name not in combined_parameters:
                        combined_parameters[param_name] = {}
                    combined_parameters[param_name].update(values)
                    
                # Slight pause between years to avoid rate-limiting
                time.sleep(1.0)
            
            # Reconstruct the original JSON structure so transform.py works perfectly
            final_payload = {
                "properties": {
                    "parameter": combined_parameters
                }
            }
            
            raw_path.write_text(json.dumps(final_payload), encoding="utf-8")
            print("ok")
            
        except Exception as exc:
            print(f"FAILED: {exc}")

        # Be polite to the public API between cities
        time.sleep(1.5)


if __name__ == "__main__":
    extract_all()