# load.py
"""Write clean data to SQLite and CSV backup."""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from config import CSV_PATH, DB_PATH


def load(df: pd.DataFrame) -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{DB_PATH}")

    df.to_sql("hourly_weather", engine, if_exists="replace", index=False, chunksize=50_000)

    df.to_csv(CSV_PATH, index=False)

    print(f"[load] SQLite  → {DB_PATH}")
    print(f"[load] CSV     → {CSV_PATH}")
    print(f"[load] rows    = {len(df):,}")


if __name__ == "__main__":
    from transform import transform_all

    load(transform_all())