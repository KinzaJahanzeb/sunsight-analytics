# app.py
"""Sunsight Analytics: ETL + EDA Pipeline"""

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
    page_title="Sunsight Analytics",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Text Color Fix */
html, body, [class*="css"], p, span, div, label {
    font-family: 'Inter', sans-serif;
    color: #cbd5e1 !important; 
}
.stApp {
    background: radial-gradient(circle at 20% 20%, #0f172a 0%, #020617 60%);
}

/* Headings */
h1, h2, h3 { 
    color: #f8fafc !important; 
    letter-spacing: -0.02em; 
}
h1 {
    background: linear-gradient(90deg, #38bdf8, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}

/* Captions & Subtitles */
.stCaption, [data-testid="stCaptionContainer"], .stMarkdown p {
    color: #94a3b8 !important; 
}

/* Metric Cards */
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
    text-transform: uppercase; 
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { 
    color: #f8fafc !important; 
    font-size: 1.8rem !important; 
    font-weight: 700 !important; 
}

/* Tabs */
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

/* Selectbox Main Box */
div[data-baseweb="select"] > div { 
    background-color: rgba(30, 41, 59, 0.85) !important; 
    border: 1px solid rgba(56, 189, 248, 0.25) !important; 
    border-radius: 12px !important; 
    color: #f8fafc !important; 
}

/* Selected City Tags (Chips) */
div[data-baseweb="select"] span {
    background-color: rgba(56, 189, 248, 0.2) !important;
    color: #38bdf8 !important;
    border-radius: 6px !important;
}

/* =========================================
   NUCLEAR OPTION: DROPDOWN MENU FIX
   ========================================= */
/* Target the popover wrapper and ALL its children */
div[data-baseweb="popover"],
div[data-baseweb="popover"] *,
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li {
    background-color: #1e293b !important;
    color: #cbd5e1 !important;
    border-color: #1e293b !important;
}

/* Force hover state to be blue */
div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] li[aria-selected="true"] {
    background-color: rgba(56, 189, 248, 0.2) !important;
    color: #f8fafc !important;
}

/* Hide the "Select all" text color issue */
div[data-baseweb="popover"] li:first-child {
    color: #94a3b8 !important;
    border-bottom: 1px solid rgba(56, 189, 248, 0.1) !important;
}

/* ========================================= */

/* Date Picker Calendar */
div[data-testid="stDateInput"] input {
    color: #f8fafc !important;
    background-color: rgba(30, 41, 59, 0.85) !important;
    border-radius: 8px !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Scrollbar */
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
    df["year"] = df["timestamp"].dt.year
    return df


# ---------------------------------------------------------------------------
# Plotly theme helpers
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#cbd5e1"),
    margin=dict(l=40, r=40, t=50, b=40),
    hoverlabel=dict(bgcolor="#1e293b", font_size=14),
)

def style(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, title=title)
    fig.update_xaxes(showgrid=False, zeroline=False) 
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.08)", zeroline=False)
    return fig


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("# Sunsight Analytics: ETL + EDA Pipeline")
st.markdown("Diagrammatic EDA of **5 years** of hourly solar and weather data for Pakistani cities.")
st.markdown("---")

# ---------------------------------------------------------------------------
# Load Data & Build Built-In Filter
# ---------------------------------------------------------------------------
df = load_data()
all_cities = sorted(df["city"].unique())

filter_col1, filter_col2 = st.columns([1, 2])

with filter_col1:
    selected_cities = st.multiselect(
        "Select Cities to Analyze:", 
        all_cities, 
        default=all_cities[:4]
    )

if not selected_cities:
    selected_cities = all_cities

fdf = df[df["city"].isin(selected_cities)].copy()

st.markdown("")

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Total Rows", f"{len(fdf):,}")
with k2:
    st.metric("Cities Selected", f"{fdf['city'].nunique()}")
with k3:
    st.metric("Mean All-Sky Irradiance", f"{fdf['irradiance_allsky'].mean():.1f} W/m²")
with k4:
    c_ratio = fdf["irradiance_allsky"].sum() / fdf["irradiance_clearsky"].sum() if fdf["irradiance_clearsky"].sum() > 0 else 0
    st.metric("Cloud Transmission", f"{c_ratio:.1%}")

st.markdown("---")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Data Quality", "🌅 Daily Cycle", "📅 Seasonal Pattern", 
    "🏙️ City Comparison", "☁️ Cloud Effect", "🔗 Correlations", 
    "📆 Yearly & Date Compare"
])

# ===========================================================================
# TAB 1 — Data Quality
# ===========================================================================
with tab1:
    st.markdown("### Data Quality Dashboard")
    st.caption("Where are the gaps, and which cities have fewer records?")
    c1, c2 = st.columns(2)

    with c1:
        counts = df.groupby("city").size().reset_index(name="rows").sort_values("rows")
        fig = px.bar(counts, x="rows", y="city", orientation="h", color="rows", color_continuous_scale="Teal", text="rows")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig.update_coloraxes(showscale=False)
        fig.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(style(fig, "Total Hourly Records per City"), use_container_width=True)

    with c2:
        weather_cols = ["irradiance_allsky", "temperature_c", "humidity_pct", "wind_speed_ms", "pressure_kpa", "rainfall_mm"]
        valid_pct = (1 - df.groupby("city")[weather_cols].apply(lambda g: g.isna().mean())) * 100
        valid_reset = valid_pct.reset_index().melt(id_vars="city", var_name="Variable", value_name="Valid %")
        
        fig = px.bar(valid_reset, x="city", y="Valid %", color="Variable", barmode="stack",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        
        fig.update_layout(
            xaxis_title="", 
            yaxis_title="% Valid Data", 
            legend_title="",
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(style(fig, "Data Completeness (% Valid) by City"), use_container_width=True)

# ===========================================================================
# TAB 2 — Daily Cycle
# ===========================================================================
with tab2:
    st.markdown("### Daily Sunlight Cycle")
    st.caption("When does sunlight arrive, and how consistent is it? (Local Solar Time)")
    hourly = fdf.groupby(["city", "hour"])["irradiance_allsky"].mean().reset_index()
    
    fig = px.line(hourly, x="hour", y="irradiance_allsky", color="city", 
                  color_discrete_sequence=px.colors.qualitative.Bold,
                  labels={"hour": "Hour of Day (LST)", "irradiance_allsky": "Irradiance (W/m²)", "city": "City"})
    fig.update_traces(line=dict(width=3))
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))
    st.plotly_chart(style(fig, "Mean Hourly Irradiance by City"), use_container_width=True)

# ===========================================================================
# TAB 3 — Seasonal Pattern
# ===========================================================================
with tab3:
    st.markdown("### Seasonal Pattern")
    st.caption("How does sunlight change across the year?")
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = fdf.groupby(["city", "month"])["irradiance_allsky"].mean().reset_index()
    monthly["month_name"] = monthly["month"].map(dict(enumerate(month_names, start=1)))

    fig = px.bar(monthly, x="month_name", y="irradiance_allsky", color="city",
                 barmode="group", category_orders={"month_name": month_names},
                 color_discrete_sequence=px.colors.qualitative.Bold,
                 labels={"month_name": "Month", "irradiance_allsky": "Mean Irradiance (W/m²)"})
    fig.update_layout(legend_title="")
    st.plotly_chart(style(fig, "Monthly Mean Irradiance"), use_container_width=True)

# ===========================================================================
# TAB 4 — City Comparison
# ===========================================================================
with tab4:
    st.markdown("### City-to-City Comparison")
    st.caption("Which cities get the most sun?")
    c1, c2 = st.columns([1, 1.2])

    with c1:
        city_stats = fdf.groupby("city")["irradiance_allsky"].mean().reset_index().sort_values("irradiance_allsky")
        fig = px.bar(city_stats, x="irradiance_allsky", y="city", orientation="h", 
                     color="irradiance_allsky", color_continuous_scale="Solar", text="irradiance_allsky")
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_coloraxes(showscale=False)
        fig.update_layout(xaxis_title="Mean Irradiance (W/m²)", yaxis_title="")
        st.plotly_chart(style(fig, "Annual Mean Irradiance Ranking"), use_container_width=True)

    with c2:
        city_sums = fdf.groupby("city")["irradiance_allsky"].sum().reset_index()
        fig = px.pie(city_sums, values="irradiance_allsky", names="city", 
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#020617', width=2)))
        fig.update_layout(showlegend=False)
        st.plotly_chart(style(fig, "Share of Total Sunlight Received"), use_container_width=True)

# ===========================================================================
# TAB 5 — Cloud Effect
# ===========================================================================
with tab5:
    st.markdown("### Cloud Effect")
    st.caption("How much does cloud cover reduce available sunlight?")
    c1, c2 = st.columns(2)

    with c1:
        ratio = fdf.groupby("city").apply(
            lambda g: g["irradiance_allsky"].sum() / g["irradiance_clearsky"].sum() if g["irradiance_clearsky"].sum() > 0 else 0
        ).reset_index(name="transmission").sort_values("transmission")
        
        fig = px.bar(ratio, x="transmission", y="city", orientation="h", 
                     color="transmission", color_continuous_scale="Teal", 
                     text=ratio["transmission"].map(lambda v: f"{v:.1%}"))
        fig.update_traces(textposition="outside")
        fig.update_coloraxes(showscale=False)
        fig.update_layout(xaxis_title="Transmission Ratio (All-Sky / Clear-Sky)", yaxis_title="", xaxis_tickformat=".0%")
        st.plotly_chart(style(fig, "Cloud Transmission Ratio by City"), use_container_width=True)

    with c2:
        total_allsky = fdf["irradiance_allsky"].sum()
        total_clearsky = fdf["irradiance_clearsky"].sum()
        cloud_loss = total_clearsky - total_allsky
        
        pie_data = pd.DataFrame({
            "Type": ["Actual Sunlight (All-Sky)", "Lost to Clouds"],
            "Energy": [total_allsky, cloud_loss]
        })
        
        fig = px.pie(pie_data, values="Energy", names="Type", hole=0.5, 
                     color="Type", color_discrete_map={"Actual Sunlight (All-Sky)": "#38bdf8", "Lost to Clouds": "#f472b6"})
        fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#020617', width=2)))
        fig.update_layout(showlegend=False)
        st.plotly_chart(style(fig, "Total Solar Energy: Available vs. Lost"), use_container_width=True)

# ===========================================================================
# TAB 6 — Correlations
# ===========================================================================
with tab6:
    st.markdown("### Correlation Overview")
    st.caption("Which weather variables move together?")
    
    weather_cols = ["irradiance_allsky", "irradiance_clearsky", "temperature_c", "humidity_pct", "wind_speed_ms", "pressure_kpa", "rainfall_mm"]
    
    corr = fdf[weather_cols].corr()["irradiance_allsky"].drop("irradiance_allsky").reset_index()
    corr.columns = ["Variable", "Correlation"]
    corr = corr.sort_values("Correlation")
    
    corr["Color"] = corr["Correlation"].apply(lambda x: "#38bdf8" if x > 0 else "#f472b6")
    
    fig = px.bar(corr, x="Correlation", y="Variable", orientation="h", text="Correlation")
    fig.update_traces(marker_color=corr["Color"], texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(xaxis_title="Correlation with All-Sky Irradiance", yaxis_title="", xaxis_range=[-1, 1])
    st.plotly_chart(style(fig, "How Weather Variables Affect Sunlight"), use_container_width=True)

# ===========================================================================
# TAB 7 — Yearly & Date Comparison
# ===========================================================================
with tab7:
    st.markdown("### Yearly & Specific Date Comparison")
    st.caption("Compare cities across different years, or look at a specific historical day.")

    st.markdown("#### 📅 Annual Average Irradiance (2020–2024)")
    
    yearly = fdf.groupby(["city", "year"])["irradiance_allsky"].mean().reset_index()
    
    fig_yearly = px.bar(
        yearly, x="year", y="irradiance_allsky", color="city",
        barmode="group", text_auto=".1f",
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"year": "Year", "irradiance_allsky": "Mean Irradiance (W/m²)", "city": "City"}
    )
    fig_yearly.update_layout(xaxis=dict(type='category'), legend_title="")
    st.plotly_chart(style(fig_yearly, "Yearly Average Irradiance by City"), use_container_width=True)

    st.markdown("---")

    st.markdown("#### 🗓️ Compare a Specific Past Date")
    available_dates = sorted(fdf["timestamp"].dt.date.unique())
    selected_date = st.date_input(
        "Pick a past date:", 
        value=available_dates[0], 
        min_value=available_dates[0], 
        max_value=available_dates[-1]
    )

    day_df = fdf[fdf["timestamp"].dt.date == selected_date]
    
    if not day_df.empty:
        fig_date = px.line(
            day_df, x="timestamp", y="irradiance_allsky", color="city",
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={"timestamp": "Time", "irradiance_allsky": "Irradiance (W/m²)", "city": "City"}
        )
        fig_date.update_traces(line=dict(width=2.5))
        fig_date.update_layout(xaxis=dict(tickformat="%H:%M"))
        st.plotly_chart(style(fig_date, f"Hourly Irradiance on {selected_date}"), use_container_width=True)
    else:
        st.warning("No data available for the selected date.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption("Data: NASA POWER Hourly API · Renewable Energy community · Local Solar Time (LST) · 2020–2024")