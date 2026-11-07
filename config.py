# config.py
"""Central configuration for Solar Power Forecaster ETL + EDA."""

CITIES = {
    "Karachi":     {"lat": 24.8607, "lon": 67.0011},
    "Lahore":      {"lat": 31.5204, "lon": 74.3587},
    "Islamabad":   {"lat": 33.6844, "lon": 73.0479},
    "Faisalabad":  {"lat": 31.4180, "lon": 73.0790},
    "Multan":      {"lat": 30.1575, "lon": 71.5249},
    "Peshawar":    {"lat": 34.0151, "lon": 71.5249},
    "Quetta":      {"lat": 30.1798, "lon": 66.9750},
    "Rawalpindi":  {"lat": 33.5651, "lon": 73.0169},
    "Hyderabad":   {"lat": 25.3960, "lon": 68.3578},
    "Gwadar":      {"lat": 25.1264, "lon": 62.3225},
}

START_YEAR = 2020
END_YEAR = 2024

PARAMETERS = [
    "ALLSKY_SFC_SW_DWN",   # All-sky surface shortwave downward irradiance (W/m²)
    "CLRSKY_SFC_SW_DWN",   # Clear-sky surface shortwave downward irradiance (W/m²)
    "T2M",                 # Temperature at 2 meters (°C)
    "RH2M",                # Relative humidity at 2 meters (%)
    "WS2M",                # Wind speed at 2 meters (m/s)
    "PS",                  # Surface pressure (kPa)
    "PRECTOTCORR",         # Precipitation corrected (mm/hr)
]

COLUMN_MAP = {
    "ALLSKY_SFC_SW_DWN": "irradiance_allsky",
    "CLRSKY_SFC_SW_DWN": "irradiance_clearsky",
    "T2M": "temperature_c",
    "RH2M": "humidity_pct",
    "WS2M": "wind_speed_ms",
    "PS": "pressure_kpa",
    "PRECTOTCORR": "rainfall_mm",
}

NASA_FILL_VALUE = -999.0

API_BASE = "https://power.larc.nasa.gov/api/temporal/hourly/point"

DB_PATH = "data/solar_forecaster.db"
CSV_PATH = "data/solar_forecaster.csv"
RAW_DIR = "data/raw"