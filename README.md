# ☀️ Sunsight Analytics - Solar Power Forecaster: ETL + EDA Pipeline

A Python tool that collects, cleans, validates, and visualizes five years of hourly weather and solar data for 10 major Pakistani cities. 

**Note:** This project focuses purely on the ETL (Extract, Transform, Load) and EDA (Exploratory Data Analysis) phases. No predictive modeling is included.

## 📊 Project Overview
- **Data Source:** NASA POWER Hourly API (Renewable Energy community)
- **Scope:** 2020-01-01 to 2024-12-31 (5 full years)
- **Cities:** Karachi, Lahore, Islamabad, Faisalabad, Multan, Peshawar, Quetta, Rawalpindi, Hyderabad, Gwadar.
- **Volume:** ~438,480 hourly records (43,848 per city) × 9 columns.

## ⚙️ ETL Architecture
1. **Extract:** `extract.py` iterates through the 10 cities, fetching data year-by-year to bypass NASA's JSON size limits. Raw JSON is cached locally to prevent redundant API calls.
2. **Transform:** `transform.py` uses `pandas` to replace NASA sentinel values (`-999`), drop duplicates, and convert timestamps to Pakistan Standard Time. Every single row is then strictly validated using **Pydantic** (e.g., `irradiance >= 0`, `humidity` between 0 and 100).
3. **Load:** `load.py` writes the validated dataset into a queryable **SQLite** database (`solar_forecaster.db`) and a CSV backup.

## 📈 Interactive Dashboard
The EDA phase is powered by a custom-styled **Streamlit** dashboard featuring dark-mode glassmorphism, Plotly charts, and 6 distinct analytical views:
1. **Data Quality:** Record counts and missing-value heatmaps.
2. **Daily Cycle:** Mean hourly irradiance (with IQR shading) to visualize the solar noon peak.
3. **Seasonal Pattern:** Month-by-hour heatmaps to capture the seasonal envelope.
4. **City Comparison:** Ranking cities by annual mean irradiance and distribution.
5. **Cloud Effect:** Clear-sky vs. all-sky scatter plots to visualize cloud attenuation.
6. **Correlations:** Pearson correlation matrices and IQR outlier counts.

## 🚀 How to Run Locally
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt