# app.py
"""Solar Power Forecaster — ETL + EDA Dashboard (no prediction)."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

from config import CSV_PATH, DB_PATH

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Solar Power Forecaster",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 20% 20%, #0f172a 0%, #020617 60%);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1120 0%, #020617 100%);
    border-right: 1px solid rgba(56, 189, 248, 0.15);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #e2e8f0;
}

h1, h2, h3 {
    color: #f1f5f9 !important;
    letter-spacing: -0.02em;
}

h1 {
    background: linear-gradient(90deg, #38bdf8, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 16px;
    padding: 18px 22px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(8px);
}

div[data-testid="stMetric"] label {
    color: #94a3b8 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

button[data-baseweb="tab"] {
    background: transparent !important;
    color: #94a3b8 !important;
    border-radius: 10px 10px 0 0;
    font-weight: 500;
    padding: 10px 18px;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 14px;
    overflow: hidden;
}

div[data-baseweb="select"] > div {
    background-color: rgba(30, 41, 59, 0.85) !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}

.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

#MainMenu, footer, header { visibility: hidden; }

.section-card {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
    border: 1px solid rgba(56, 189, 248, 0.12);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #020617; }
::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: #334155; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if Path(DB_PATH).exists():
        engine = create_engine(f"sqlite:///{DB_PATH}")
        df = pd.read_sql_table("hourly_weather", engine)
    elif Path(CSV_PATH).exists():
        df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
    else:
        st.error("No data found. Run `python pipeline.py` first.")
        st.stop()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["month"] = df["timestamp"].dt.month
    df["hour"] = df["timestamp"].dt.hour
    return df


# ---------------------------------------------------------------------------
# Plotly theme helper
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#cbd5e1"),
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor="#1e293b", font_size=13),
)


def style(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.08)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.08)", zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ☀️ Solar Power Forecaster")
    st.caption("ETL + EDA · NASA POWER 2020–2024")
    st.markdown("---")

    df = load_data()

    all_cities = sorted(df["city"].unique())
    selected_cities = st.multiselect(
        "Cities", all_cities, default=all_cities[:3]
    )

    if not selected_cities:
        selected_cities = all_cities

    st.markdown("---")
    st.caption(
        f"**{len(df):,}** rows · **{df['city'].nunique()}** cities · "
        f"**{df['timestamp'].min():%Y}–{df['timestamp'].max():%Y}**"
    )

# Filter
fdf = df[df["city"].isin(selected_cities)].copy()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("# Solar Power Forecaster")
st.markdown(
    "Diagrammatic EDA of **5 years** of hourly solar and weather data "
    "for Pakistani cities. No prediction — only insight."
)
st.markdown("---")

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("Total Rows", f"{len(fdf):,}")

with k2:
    st.metric("Cities Selected", f"{fdf['city'].nunique()}")

with k3:
    mean_irr = fdf["irradiance_allsky"].mean()
    st.metric("Mean All-Sky Irradiance", f"{mean_irr:.1f} W/m²")

with k4:
    cloud_ratio = (
        fdf["irradiance_allsky"].sum() / fdf["irradiance_clearsky"].sum()
        if fdf["irradiance_clearsky"].sum() > 0 else 0
    )
    st.metric("Cloud Transmission", f"{cloud_ratio:.1%}")

st.markdown("")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Data Quality",
    "🌅 Daily Cycle",
    "📅 Seasonal Pattern",
    "🏙️ City Comparison",
    "☁️ Cloud Effect",
    "🔗 Correlations",
])

# ===========================================================================
# TAB 1 — Data Quality
# ===========================================================================
with tab1:
    st.markdown("### Data Quality Dashboard")
    st.caption("Where are the gaps, and which cities have fewer records?")

    c1, c2 = st.columns(2)

    with c1:
        counts = df.groupby("city").size().reset_index(name="rows")
        fig = px.bar(
            counts.sort_values("rows"),
            x="rows", y="city", orientation="h",
            color="rows", color_continuous_scale="Teal",
            text="rows",
        )
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style(fig, "Hourly Records per City"), use_container_width=True)

    with c2:
        weather_cols = [
            "irradiance_allsky", "irradiance_clearsky", "temperature_c",
            "humidity_pct", "wind_speed_ms", "pressure_kpa", "rainfall_mm",
        ]
        missing = df.groupby("city")[weather_cols].apply(lambda g: g.isna().mean() * 100)
        fig = px.imshow(
            missing,
            aspect="auto",
            color_continuous_scale="Reds",
            labels=dict(x="Variable", y="City", color="% Missing"),
        )
        fig.update_coloraxes(colorbar_ticksuffix="%")
        st.plotly_chart(style(fig, "Missing Values (%) by City & Variable"), use_container_width=True)

# ===========================================================================
# TAB 2 — Daily Cycle
# ===========================================================================
with tab2:
    st.markdown("### Daily Sunlight Cycle")
    st.caption("When does sunlight arrive, and how consistent is it?")

    hourly = (
        fdf.groupby(["city", "hour"])["irradiance_allsky"]
        .agg(["mean", lambda s: s.quantile(0.25), lambda s: s.quantile(0.75)])
        .reset_index()
    )
    hourly.columns = ["city", "hour", "mean", "q25", "q75"]

    fig = go.Figure()
    palette = px.colors.qualitative.Bold

    for i, city in enumerate(selected_cities):
        sub = hourly[hourly["city"] == city]
        color = palette[i % len(palette)]

        fig.add_trace(go.Scatter(
            x=sub["hour"], y=sub["q75"],
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=sub["hour"], y=sub["q25"],
            mode="lines", line=dict(width=0),
            fill="tonexty", fillcolor=color.replace("rgb", "rgba").replace(")", ",0.12)"),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=sub["hour"], y=sub["mean"],
            mode="lines", name=city,
            line=dict(color=color, width=2.5),
        ))

    fig.update_layout(xaxis_title="Hour of Day (LST)", yaxis_title="Irradiance (W/m²)")
    st.plotly_chart(style(fig, "Mean Hourly All-Sky Irradiance (shaded = IQR)"), use_container_width=True)

# ===========================================================================
# TAB 3 — Seasonal Pattern
# ===========================================================================
with tab3:
    st.markdown("### Seasonal Pattern")
    st.caption("How does sunlight change across the year?")

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    pivot = (
        fdf.groupby(["city", "month", "hour"])["irradiance_allsky"]
        .mean()
        .reset_index()
    )

    n_cols = 5
    rows = (len(selected_cities) + n_cols - 1) // n_cols

    for r in range(rows):
        cols = st.columns(n_cols)
        for c in range(n_cols):
            idx = r * n_cols + c
            if idx >= len(selected_cities):
                continue
            city = selected_cities[idx]
            sub = pivot[pivot["city"] == city]
            z = sub.pivot(index="month", columns="hour", values="irradiance_allsky")
            z = z.reindex(columns=range(24))

            with cols[c]:
                fig = px.imshow(
                    z,
                    aspect="auto",
                    color_continuous_scale="Inferno",
                    labels=dict(x="Hour", y="Month", color="W/m²"),
                )
                fig.update_yaxes(
                    tickvals=list(range(12)),
                    ticktext=month_names,
                )
                fig.update_coloraxes(showscale=False)
                fig.update_layout(title=city, height=220, margin=dict(l=20, r=20, t=35, b=20))
                st.plotly_chart(fig, use_container_width=True)

    monthly = fdf.groupby(["city", "month"])["irradiance_allsky"].mean().reset_index()
    monthly["month_name"] = monthly["month"].map(dict(enumerate(month_names, start=1)))

    fig = px.bar(
        monthly, x="month_name", y="irradiance_allsky", color="city",
        barmode="group", category_orders={"month_name": month_names},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_layout(xaxis_title="", yaxis_title="Mean Irradiance (W/m²)", legend_title="")
    st.plotly_chart(style(fig, "Monthly Mean Irradiance"), use_container_width=True)

# ===========================================================================
# TAB 4 — City Comparison
# ===========================================================================
with tab4:
    st.markdown("### City-to-City Comparison")
    st.caption("Which cities get the most sun?")

    c1, c2 = st.columns(2)

    with c1:
        city_stats = (
            fdf.groupby("city")["irradiance_allsky"]
            .agg(["mean", "std"])
            .reset_index()
            .sort_values("mean", ascending=True)
        )
        fig = px.bar(
            city_stats, x="mean", y="city", orientation="h",
            error_x="std", color="mean",
            color_continuous_scale="Solar",
        )
        fig.update_coloraxes(showscale=False)
        fig.update_layout(xaxis_title="Mean Irradiance (W/m²)", yaxis_title="")
        st.plotly_chart(style(fig, "Annual Mean Irradiance (error = std dev)"), use_container_width=True)

    with c2:
        fig = px.box(
            fdf, x="city", y="irradiance_allsky",
            color="city",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig.update_layout(xaxis_title="", yaxis_title="Irradiance (W/m²)", showlegend=False)
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(style(fig, "Distribution of Hourly Irradiance"), use_container_width=True)

# ===========================================================================
# TAB 5 — Cloud Effect
# ===========================================================================
with tab5:
    st.markdown("### Cloud Effect")
    st.caption("How much does cloud cover reduce available sunlight?")

    c1, c2 = st.columns([1.2, 1])

    with c1:
        sample = fdf.sample(min(5000, len(fdf)), random_state=42)
        fig = px.scatter(
            sample, x="irradiance_clearsky", y="irradiance_allsky",
            color="city", opacity=0.35,
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={
                "irradiance_clearsky": "Clear-Sky Irradiance (W/m²)",
                "irradiance_allsky": "All-Sky Irradiance (W/m²)",
            },
        )
        max_val = max(sample["irradiance_clearsky"].max(), sample["irradiance_allsky"].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode="lines", name="No-Cloud Ceiling",
            line=dict(color="#f472b6", dash="dash", width=1.5),
        ))
        st.plotly_chart(style(fig, "Clear-Sky vs All-Sky (sample of 5,000 hours)"), use_container_width=True)

    with c2:
        ratio = (
            fdf.groupby("city")
            .apply(lambda g: g["irradiance_allsky"].sum() / g["irradiance_clearsky"].sum()
                   if g["irradiance_clearsky"].sum() > 0 else 0)
            .reset_index(name="transmission")
            .sort_values("transmission")
        )
        fig = px.bar(
            ratio, x="transmission", y="city", orientation="h",
            color="transmission", color_continuous_scale="Teal",
            text=ratio["transmission"].map(lambda v: f"{v:.1%}"),
        )
        fig.update_traces(textposition="outside")
        fig.update_coloraxes(showscale=False)
        fig.update_layout(xaxis_title="All-Sky / Clear-Sky Ratio", yaxis_title="", xaxis_tickformat=".0%")
        st.plotly_chart(style(fig, "Cloud Transmission Ratio by City"), use_container_width=True)

# ===========================================================================
# TAB 6 — Correlations
# ===========================================================================
with tab6:
    st.markdown("### Correlation & Outlier Overview")
    st.caption("Which weather variables move together?")

    c1, c2 = st.columns(2)

    weather_cols = [
        "irradiance_allsky", "irradiance_clearsky", "temperature_c",
        "humidity_pct", "wind_speed_ms", "pressure_kpa", "rainfall_mm",
    ]

    with c1:
        corr = fdf[weather_cols].corr()
        fig = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        )
        fig.update_layout(height=500)
        st.plotly_chart(style(fig, "Pearson Correlation Matrix"), use_container_width=True)

    with c2:
        outlier_counts = {}
        for col in weather_cols:
            s = fdf[col].dropna()
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outlier_counts[col] = int(((s < lo) | (s > hi)).sum())

        odf = pd.DataFrame(
            list(outlier_counts.items()), columns=["variable", "outliers"]
        ).sort_values("outliers", ascending=True)

        fig = px.bar(
            odf, x="outliers", y="variable", orientation="h",
            color="outliers", color_continuous_scale="Oranges",
            text="outliers",
        )
        fig.update_traces(textposition="outside")
        fig.update_coloraxes(showscale=False)
        fig.update_layout(xaxis_title="Count (1.5 × IQR rule)", yaxis_title="")
        st.plotly_chart(style(fig, "Outlier Count per Variable"), use_container_width=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "Data: NASA POWER Hourly API · Renewable Energy community · "
    "Local Solar Time (LST) · 2020–2024 · No prediction model included."
)