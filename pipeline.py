# pipeline.py
"""One-shot ETL runner: extract → transform → load."""

from extract import extract_all
from load import load
from transform import transform_all

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1/3  Extract")
    print("=" * 60)
    extract_all()

    print("\n" + "=" * 60)
    print("STEP 2/3  Transform")
    print("=" * 60)
    df = transform_all()

    print("\n" + "=" * 60)
    print("STEP 3/3  Load")
    print("=" * 60)
    load(df)

    print("\nDone.")