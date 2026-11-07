# transform.py
"""Clean, validate, and merge raw NASA POWER data."""

import json
from pathlib import Path

import pandas as pd
from pydantic import BaseModel, Field, ValidationError

from config import (
    CITIES,
    COLUMN_MAP,
    NASA_FILL_VALUE,
    PARAMETERS,
    RAW_DIR,
)


class WeatherRecord(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    city: str
    timestamp: pd.Timestamp
    irradiance_allsky: float = Field(ge=0)
    irradiance_clearsky: float = Field(ge=0)
    temperature_c: float
    humidity_pct: float = Field(ge=0, le=100)
    wind_speed_ms: float = Field(ge=0)
    pressure_kpa: float = Field(gt=50, lt=120)
    rainfall_mm: float = Field(ge=0)


def _parse_city(raw_path: Path, city: str) -> pd.DataFrame:
    """Turn one raw JSON file into a clean DataFrame."""
    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    param_block = payload["properties"]["parameter"]

    # NASA returns dicts keyed by "YYYYMMDDHH"
    df = pd.DataFrame(param_block)
    df.index = pd.to_datetime(df.index, format="%Y%m%d%H")
    
    # Convert to Pakistan Standard Time
    df.index = df.index.tz_localize("UTC").tz_convert("Asia/Karachi").tz_localize(None)
    df.index.name = "timestamp"

    # Rename to friendly names
    df = df.rename(columns=COLUMN_MAP)

    # Replace NASA sentinel with NaN
    df = df.replace(NASA_FILL_VALUE, pd.NA)

    # Drop rows where every weather value is missing
    df = df.dropna(how="all")

    df = df.reset_index()
    df.insert(0, "city", city)

    return df


def _validate(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Row-wise Pydantic validation; return valid rows + rejection log."""
    valid_rows = []
    rejected = []

    df = df.copy()
    
    # Fill missing values so Pydantic doesn't crash on pd.NA
    for col in ["irradiance_allsky", "irradiance_clearsky", "wind_speed_ms", "rainfall_mm"]:
        df[col] = df[col].fillna(0.0)
    
    for col, fallback in [("temperature_c", 25.0), ("humidity_pct", 50.0), ("pressure_kpa", 101.3)]:
        df[col] = df[col].interpolate().fillna(fallback)

    for _, row in df.iterrows():
        record = row.to_dict()
        try:
            WeatherRecord(**record)
            valid_rows.append(record)
        except ValidationError as exc:
            rejected.append({"city": record["city"], "timestamp": record["timestamp"],
                             "errors": exc.errors()})

    return pd.DataFrame(valid_rows), rejected


def transform_all() -> pd.DataFrame:
    """Load every cached city file, clean, validate, and concatenate."""
    frames = []

    for city in CITIES:
        raw_path = Path(RAW_DIR) / f"{city}.json"
        if not raw_path.exists():
            print(f"[warn] missing raw file for {city}")
            continue

        print(f"[transform] {city} ...", end=" ", flush=True)
        df = _parse_city(raw_path, city)

        # Drop duplicates on (city, timestamp)
        before = len(df)
        df = df.drop_duplicates(subset=["city", "timestamp"], keep="first")
        dupes = before - len(df)

        clean, rejected = _validate(df)
        print(f"{len(clean):,} valid, {dupes} dupes, {len(rejected)} rejected")

        frames.append(clean)

    if not frames:
        raise RuntimeError("No valid data found. Run extract.py first.")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.sort_values(["city", "timestamp"]).reset_index(drop=True)

    # Cast timestamp properly
    combined["timestamp"] = pd.to_datetime(combined["timestamp"])

    print(f"\nTotal: {len(combined):,} rows × {len(combined.columns)} columns")
    return combined


if __name__ == "__main__":
    df = transform_all()
    print(df.head())