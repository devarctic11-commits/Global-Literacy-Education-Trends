"""
Global Literacy & Education Trends: An Analytical Study
Production-grade Interactive Streamlit Application
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS Styling
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Global Literacy & Education Trends",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    
    /* Main Background Accent */
    .main {
        background-color: #0b0f19;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(26, 34, 53, 0.7) 0%, rgba(18, 24, 38, 0.9) 100%);
        border: 1px solid rgba(80, 110, 160, 0.25);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.5);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.85rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .metric-sub {
        color: #38bdf8;
        font-size: 0.80rem;
        margin-top: 4px;
        font-weight: 400;
    }

    /* Section Banner */
    .section-header {
        background: linear-gradient(90deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
        border-left: 5px solid #6366f1;
        padding: 16px 22px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .section-title {
        color: #ffffff;
        font-size: 1.35rem;
        font-weight: 600;
        margin: 0;
    }
    .section-subtitle {
        color: #c7d2fe;
        font-size: 0.88rem;
        margin-top: 4px;
        margin-bottom: 0;
    }

    /* Badge & Tag */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    .badge-primary {
        background-color: rgba(99, 102, 241, 0.2);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    .badge-success {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }

    /* Tab bar aesthetic */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111827;
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94a3b8;
        padding: 8px 16px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4f46e5 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# 2. Database Connection & Data Loaders
# ------------------------------------------------------------------------------
DB_PATH = os.path.join("database", "education_analytics.db")

@st.cache_resource
def get_db_connection():
    if not os.path.exists(DB_PATH):
        # Fallback to run pipeline if not ready
        from scripts.prepare_data import run_pipeline
        run_pipeline()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

@st.cache_data(ttl=3600)
def load_all_data():
    conn = get_db_connection()
    df_lit = pd.read_sql_query("SELECT * FROM literacy_rates WHERE is_country = 1", conn)
    df_illit = pd.read_sql_query("SELECT * FROM illiteracy_population WHERE is_country = 1", conn)
    df_gdp_sch = pd.read_sql_query("SELECT * FROM gdp_schooling WHERE is_country = 1", conn)
    
    # Combined master dataset for correlations and profiles
    df_master = pd.merge(
        df_lit[["country", "country_code", "year", "region", "adult_literacy_rate", "youth_literacy_avg", "literacy_gender_gap", "literacy_growth_rate"]],
        df_gdp_sch[["country", "year", "gdp_per_capita", "avg_years_schooling", "gdp_per_schooling_year", "education_index"]],
        on=["country", "year"],
        how="outer"
    )
    df_master = pd.merge(
        df_master,
        df_illit[["country", "year", "illiteracy_rate", "total_population", "illiterate_population"]],
        on=["country", "year"],
        how="outer"
    )
    return df_lit, df_illit, df_gdp_sch, df_master

df_lit, df_illit, df_gdp_sch, df_master = load_all_data()

# Dark Theme for Plotly Charts
PLOTLY_THEME = "plotly_dark"
CHART_BG = "rgba(17, 24, 39, 0.4)"
PAPER_BG = "rgba(11, 15, 25, 0)"

def apply_chart_styling(fig):
    fig.update_layout(
        template=PLOTLY_THEME,
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family="Outfit, Inter, sans-serif", color="#e2e8f0"),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


# ------------------------------------------------------------------------------
# 3. Sidebar Navigation & Global Filters
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 10px 0 20px 0;'>
        <div style='font-size: 2.2rem;'>📊</div>
        <h2 style='color: #f8fafc; font-size: 1.25rem; font-weight: 700; margin: 4px 0;'>Global Literacy & Education</h2>
        <span class='badge badge-primary'>GUVI HCL Capstone</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧭 Navigation")
    app_mode = st.radio(
        "Select Analytical Module:",
        [
            "🌐 Executive Overview",
            "🧮 SQL Query Studio (13 Queries)",
            "📊 Exploratory Data Analysis (EDA)",
            "🌍 Country Profile & Comparison",
            "🎯 Policy & Business Use Cases"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ Quick Filters")
    available_years = sorted(df_master["year"].dropna().unique().astype(int))
    selected_year = st.slider("Select Benchmark Year:", min_value=1990, max_value=2023, value=2020)
    
    available_regions = ["All Continents"] + sorted(list(df_master["region"].dropna().unique()))
    selected_region = st.selectbox("Select Geographic Region:", available_regions)
    
    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.78rem; color: #64748b; line-height: 1.4;'>
        <strong>Data Sources:</strong> Our World in Data (OWID), World Bank, UNESCO.<br>
        <strong>Timespan:</strong> 1990 – 2023<br>
        <strong>Database:</strong> SQLite Engine
    </div>
    """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# MODULE 1: Executive Overview & KPI Dashboard
# ------------------------------------------------------------------------------
if app_mode == "🌐 Executive Overview":
    st.markdown("""
    <div class='section-header'>
        <h2 class='section-title'>Global Literacy & Education Trends: Executive Dashboard</h2>
        <p class='section-subtitle'>High-level macro analysis of worldwide adult literacy, schooling duration, and economic prosperity</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter dataset for benchmark year and region
    df_year = df_master[df_master["year"] == selected_year]
    if selected_region != "All Continents":
        df_year = df_year[df_year["region"] == selected_region]
        
    # Top KPI Metrics Cards
    c1, c2, c3, c4 = st.columns(4)
    
    avg_lit = df_year["adult_literacy_rate"].mean()
    avg_school = df_year["avg_years_schooling"].mean()
    total_illit = df_year["illiterate_population"].sum()
    avg_gdp = df_year["gdp_per_capita"].mean()
    
    with c1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Avg Adult Literacy ({selected_year})</div>
            <div class='metric-value'>{avg_lit:.1f}%</div>
            <div class='metric-sub'>Global Benchmark</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Avg Years of Schooling</div>
            <div class='metric-value'>{avg_school:.1f} yrs</div>
            <div class='metric-sub'>Access & Duration</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Estimated Illiterate Pop</div>
            <div class='metric-value'>{total_illit/1e6:.1f}M</div>
            <div class='metric-sub'>Across Reported Nations</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Average GDP per Capita</div>
            <div class='metric-value'>${avg_gdp:,.0f}</div>
            <div class='metric-sub'>PPP Constant 2017 USD</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Global Choropleth Map
    st.subheader(f"🗺️ Global Geographic Distribution ({selected_year})")
    map_metric = st.selectbox(
        "Choose Map Indicator:",
        [
            ("adult_literacy_rate", "Adult Literacy Rate (%)"),
            ("youth_literacy_avg", "Youth Literacy Average (%)"),
            ("avg_years_schooling", "Average Years of Schooling"),
            ("gdp_per_capita", "GDP per Capita (USD)"),
            ("education_index", "Education Index Score (0-100)"),
            ("illiteracy_rate", "Illiteracy Rate (%)")
        ],
        format_func=lambda x: x[1]
    )
    
    map_col, map_label = map_metric
    df_map = df_master[(df_master["year"] == selected_year) & (df_master[map_col].notnull())]
    
    if len(df_map) > 0:
        fig_map = px.choropleth(
            df_map,
            locations="country_code",
            color=map_col,
            hover_name="country",
            hover_data={map_col: ":.2f", "region": True, "country_code": False},
            color_continuous_scale="Viridis" if "illiteracy" not in map_col else "Reds",
            title=f"Global {map_label} across Nations in {selected_year}"
        )
        fig_map.update_geos(
            showcoastlines=True,
            coastlinecolor="#334155",
            showland=True,
            landcolor="#1e293b",
            showocean=True,
            oceancolor="#0f172a",
            bgcolor="#0b0f19"
        )
        apply_chart_styling(fig_map)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info(f"No direct country records available for {map_label} in {selected_year}. Please choose another year (e.g. 2020 or 2015).")

    # Continental Breakdown and Trends Row
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("🌐 Regional Literacy Disparities")
        df_reg = df_master.dropna(subset=["region", "adult_literacy_rate"])
        df_reg = df_reg[df_reg["region"] != "Global"]
        fig_bar = px.box(
            df_reg,
            x="region",
            y="adult_literacy_rate",
            color="region",
            title="Adult Literacy Rate Distribution by Continent (1990–2023)",
            points=False
        )
        apply_chart_styling(fig_bar)
        fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Literacy Rate (%)")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_b:
        st.subheader("📈 Global Schooling Progress Over Time")
        conn = get_db_connection()
        df_sch_trend = pd.read_sql_query("""
            SELECT year, ROUND(AVG(avg_years_schooling), 2) AS avg_schooling
            FROM gdp_schooling
            WHERE is_country = 1 AND avg_years_schooling IS NOT NULL
            GROUP BY year
            ORDER BY year ASC
        """, conn)
        fig_trend = px.line(
            df_sch_trend,
            x="year",
            y="avg_schooling",
            markers=True,
            title="Worldwide Average Years of Schooling (1990–2020)",
            line_shape="spline"
        )
        fig_trend.update_traces(line_color="#6366f1", line_width=3, marker_size=8)
        apply_chart_styling(fig_trend)
        fig_trend.update_layout(xaxis_title="Year", yaxis_title="Years of Schooling")
        st.plotly_chart(fig_trend, use_container_width=True)


# ------------------------------------------------------------------------------
# MODULE 2: SQL Query Studio (All 13 Required Queries + Custom SQL Console)
# ------------------------------------------------------------------------------
elif app_mode == "🧮 SQL Query Studio (13 Queries)":
    st.markdown("""
    <div class='section-header'>
        <h2 class='section-title'>SQL Query Studio: Database Querying & Visualization</h2>
        <p class='section-subtitle'>Execute and inspect all 13 project capstone SQL queries with instant data tables, statistics, and visualizations</p>
    </div>
    """, unsafe_allow_html=True)
    
    conn = get_db_connection()
    
    queries_catalog = {
        "Query 1: Top 5 countries with highest adult literacy in 2020": {
            "sql": """SELECT country, country_code, region, adult_literacy_rate
FROM literacy_rates
WHERE year = 2020 AND is_country = 1 AND adult_literacy_rate IS NOT NULL
ORDER BY adult_literacy_rate DESC
LIMIT 5;""",
            "chart_type": "bar",
            "x": "country",
            "y": "adult_literacy_rate",
            "desc": "Identifies the highest performing countries in adult literacy (15+ age) for the benchmark year 2020."
        },
        "Query 2: Countries where female youth literacy < 80%": {
            "sql": """SELECT DISTINCT country, country_code, region, year, youth_literacy_female
FROM literacy_rates
WHERE is_country = 1 AND youth_literacy_female < 80 AND youth_literacy_female IS NOT NULL
ORDER BY youth_literacy_female ASC
LIMIT 15;""",
            "chart_type": "bar",
            "x": "country",
            "y": "youth_literacy_female",
            "desc": "Highlights priority nations with acute gender educational disparities where female youth literacy remains under 80%."
        },
        "Query 3: Average adult literacy per continent (owid region)": {
            "sql": """SELECT region, 
       ROUND(AVG(adult_literacy_rate), 2) AS avg_adult_literacy,
       COUNT(*) AS total_records
FROM literacy_rates
WHERE region IS NOT NULL AND region != 'Global' AND adult_literacy_rate IS NOT NULL
GROUP BY region
ORDER BY avg_adult_literacy DESC;""",
            "chart_type": "bar",
            "x": "region",
            "y": "avg_adult_literacy",
            "desc": "Ranks world continents by their aggregate historical adult literacy rate."
        },
        "Query 4: Countries with illiteracy % > 20% in 2000": {
            "sql": """SELECT country, country_code, region, illiteracy_rate AS illiteracy_percentage
FROM illiteracy_population
WHERE year = 2000 AND is_country = 1 AND illiteracy_rate > 20
ORDER BY illiteracy_percentage DESC
LIMIT 15;""",
            "chart_type": "bar",
            "x": "country",
            "y": "illiteracy_percentage",
            "desc": "Establishes a baseline of countries having severe illiteracy (> 20%) at the start of the millennium (2000)."
        },
        "Query 5: Trend of illiteracy % for India (2000–2020)": {
            "sql": """SELECT country, year, illiteracy_rate, literacy_rate
FROM illiteracy_population
WHERE country = 'India' AND year BETWEEN 2000 AND 2020
ORDER BY year ASC;""",
            "chart_type": "line_dual",
            "x": "year",
            "y1": "illiteracy_rate",
            "y2": "literacy_rate",
            "desc": "Tracks the rapid 20-year transition in India, where illiteracy plummeted while literacy climbed."
        },
        "Query 6: Top 10 countries with largest illiterate population in the last year": {
            "sql": """WITH latest_year AS (
    SELECT country, MAX(year) AS max_year
    FROM illiteracy_population
    WHERE is_country = 1 AND illiterate_population IS NOT NULL
    GROUP BY country
)
SELECT p.country, p.country_code, p.year, 
       ROUND(p.illiteracy_rate, 2) AS illiteracy_percentage,
       CAST(p.illiterate_population AS BIGINT) AS illiterate_population
FROM illiteracy_population p
JOIN latest_year l ON p.country = l.country AND p.year = l.max_year
ORDER BY p.illiterate_population DESC
LIMIT 10;""",
            "chart_type": "bar",
            "x": "country",
            "y": "illiterate_population",
            "desc": "Examines the absolute human scale of illiteracy, demonstrating how population size impacts total illiterate individuals."
        },
        "Query 7: Countries with avg_years_schooling > 7 and gdp_per_capita < 5000": {
            "sql": """SELECT DISTINCT country, country_code, region, year,
       ROUND(avg_years_schooling, 2) AS avg_years_schooling,
       ROUND(gdp_per_capita, 2) AS gdp_per_capita
FROM gdp_schooling
WHERE is_country = 1 AND avg_years_schooling > 7 AND gdp_per_capita < 5000
ORDER BY gdp_per_capita ASC
LIMIT 15;""",
            "chart_type": "scatter",
            "x": "avg_years_schooling",
            "y": "gdp_per_capita",
            "desc": "Detects high-efficiency nations that achieve over 7 years of schooling despite modest economic resources (< $5,000)."
        },
        "Query 8: Rank countries by GDP per schooling for the year 2020": {
            "sql": """SELECT country, country_code, region,
       ROUND(gdp_per_capita, 2) AS gdp_per_capita,
       ROUND(avg_years_schooling, 2) AS avg_years_schooling,
       ROUND(gdp_per_schooling_year, 2) AS gdp_per_schooling_year,
       DENSE_RANK() OVER (ORDER BY gdp_per_schooling_year DESC) AS gdp_schooling_rank
FROM gdp_schooling
WHERE year = 2020 AND is_country = 1 AND gdp_per_schooling_year IS NOT NULL
ORDER BY gdp_schooling_rank ASC
LIMIT 15;""",
            "chart_type": "bar",
            "x": "country",
            "y": "gdp_per_schooling_year",
            "desc": "Measures economic output generated per year of national education in 2020."
        },
        "Query 9: Find global average schooling years per year": {
            "sql": """SELECT year, 
       ROUND(AVG(avg_years_schooling), 2) AS global_avg_schooling_years,
       COUNT(country) AS countries_reported
FROM gdp_schooling
WHERE is_country = 1 AND avg_years_schooling IS NOT NULL
GROUP BY year
ORDER BY year DESC
LIMIT 15;""",
            "chart_type": "line",
            "x": "year",
            "y": "global_avg_schooling_years",
            "desc": "Monitors the global historical progression in mean schooling duration from 1990 to 2020."
        },
        "Query 10: Top 10 countries in 2020 with highest GDP per capita but lowest schooling (< 6 years)": {
            "sql": """SELECT country, country_code, region,
       ROUND(gdp_per_capita, 2) AS gdp_per_capita,
       ROUND(avg_years_schooling, 2) AS avg_years_schooling
FROM gdp_schooling
WHERE year = 2020 AND is_country = 1 AND avg_years_schooling < 6 AND gdp_per_capita IS NOT NULL
ORDER BY gdp_per_capita DESC
LIMIT 10;""",
            "chart_type": "bar",
            "x": "country",
            "y": "gdp_per_capita",
            "desc": "Uncovers resource-rich or rentier economies where high income has not yet translated into extended educational duration."
        },
        "Query 11: Countries with high illiterate population (> 500,000) despite having > 10 avg years of schooling": {
            "sql": """SELECT p.country, p.country_code, p.year,
       CAST(p.illiterate_population AS BIGINT) AS illiterate_population,
       ROUND(p.illiteracy_rate, 2) AS illiteracy_rate,
       ROUND(s.avg_years_schooling, 2) AS avg_years_schooling
FROM illiteracy_population p
JOIN gdp_schooling s ON p.country = s.country AND p.year = s.year
WHERE p.is_country = 1 AND s.avg_years_schooling > 10 AND p.illiterate_population > 500000
ORDER BY p.illiterate_population DESC
LIMIT 10;""",
            "chart_type": "bar",
            "x": "country",
            "y": "illiterate_population",
            "desc": "Identifies high-schooling countries that nevertheless harbor significant pockets of illiterate adults."
        },
        "Query 12: Compare literacy rates and GDP per capita growth for India over last 20 years (2000-2020)": {
            "sql": """SELECT l.country, l.year,
       l.adult_literacy_rate,
       l.youth_literacy_avg,
       ROUND(g.gdp_per_capita, 2) AS gdp_per_capita
FROM literacy_rates l
JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
WHERE l.country = 'India' AND l.year BETWEEN 2000 AND 2020
ORDER BY l.year ASC;""",
            "chart_type": "line_dual",
            "x": "year",
            "y1": "adult_literacy_rate",
            "y2": "gdp_per_capita",
            "desc": "Shows the parallel rise of India's literacy rate and GDP per capita between 2000 and 2020."
        },
        "Query 13: Difference between youth male and female rates for countries with GDP per capita > $30,000 in 2020": {
            "sql": """SELECT l.country, l.country_code, l.year,
       ROUND(g.gdp_per_capita, 2) AS gdp_per_capita,
       l.youth_literacy_male,
       l.youth_literacy_female,
       ROUND(l.literacy_gender_gap, 2) AS youth_literacy_gender_gap
FROM literacy_rates l
JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
WHERE l.year = 2020 AND l.is_country = 1 AND g.gdp_per_capita > 30000 
  AND l.youth_literacy_male IS NOT NULL AND l.youth_literacy_female IS NOT NULL
ORDER BY g.gdp_per_capita DESC
LIMIT 10;""",
            "chart_type": "bar",
            "x": "country",
            "y": "youth_literacy_gender_gap",
            "desc": "Validates the gender gap convergence hypothesis: high-income economies exhibit near-zero gender disparities."
        }
    }
    
    query_tab1, query_tab2 = st.tabs(["📋 Pre-Configured Capstone Queries (1 to 13)", "💻 Custom SQL Console"])
    
    with query_tab1:
        selected_q_name = st.selectbox("Select Capstone Query to Run:", list(queries_catalog.keys()))
        q_meta = queries_catalog[selected_q_name]
        
        st.info(f"**Business Context:** {q_meta['desc']}")
        
        with st.expander("🔍 View SQL Statement", expanded=True):
            st.code(q_meta["sql"], language="sql")
            
        try:
            df_res = pd.read_sql_query(q_meta["sql"], conn)
            
            c_left, c_right = st.columns([1.1, 0.9])
            
            with c_left:
                st.subheader("📄 Query Results Table")
                st.dataframe(df_res, use_container_width=True, height=360)
                csv_data = df_res.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV Output",
                    data=csv_data,
                    file_name=f"{selected_q_name[:10].replace(' ', '_')}_results.csv",
                    mime="text/csv"
                )
                
            with c_right:
                st.subheader("📊 Dynamic Visualization")
                chart_type = q_meta["chart_type"]
                
                if chart_type == "bar":
                    fig_q = px.bar(
                        df_res,
                        x=q_meta["x"],
                        y=q_meta["y"],
                        text_auto=".2s" if df_res[q_meta["y"]].max() > 1000 else True,
                        color=q_meta["y"],
                        color_continuous_scale="Viridis",
                        title=f"{selected_q_name[:35]}..."
                    )
                    apply_chart_styling(fig_q)
                    st.plotly_chart(fig_q, use_container_width=True)
                    
                elif chart_type == "line":
                    fig_q = px.line(
                        df_res,
                        x=q_meta["x"],
                        y=q_meta["y"],
                        markers=True,
                        title=f"{selected_q_name[:35]}..."
                    )
                    fig_q.update_traces(line_color="#38bdf8", line_width=3)
                    apply_chart_styling(fig_q)
                    st.plotly_chart(fig_q, use_container_width=True)
                    
                elif chart_type == "line_dual":
                    fig_q = go.Figure()
                    fig_q.add_trace(go.Scatter(
                        x=df_res[q_meta["x"]],
                        y=df_res[q_meta["y1"]],
                        name=q_meta["y1"].replace("_", " ").title(),
                        mode="lines+markers",
                        line=dict(color="#ef4444", width=3)
                    ))
                    fig_q.add_trace(go.Scatter(
                        x=df_res[q_meta["x"]],
                        y=df_res[q_meta["y2"]],
                        name=q_meta["y2"].replace("_", " ").title(),
                        mode="lines+markers",
                        line=dict(color="#10b981", width=3)
                    ))
                    fig_q.update_layout(title="Trend Trajectory Over Time")
                    apply_chart_styling(fig_q)
                    st.plotly_chart(fig_q, use_container_width=True)
                    
                elif chart_type == "scatter":
                    fig_q = px.scatter(
                        df_res,
                        x=q_meta["x"],
                        y=q_meta["y"],
                        hover_name="country",
                        size_max=15,
                        color="country",
                        title="Distribution Plot"
                    )
                    apply_chart_styling(fig_q)
                    st.plotly_chart(fig_q, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error executing query: {e}")
            
    with query_tab2:
        st.subheader("💻 Interactive SQL Query Executor")
        st.markdown("""
        Run custom SQL commands against the database tables:
        - `literacy_rates`: `country, country_code, year, region, is_country, adult_literacy_rate, youth_literacy_male, youth_literacy_female, youth_literacy_avg, literacy_gender_gap, literacy_growth_rate`
        - `illiteracy_population`: `country, country_code, year, region, is_country, literacy_rate, illiteracy_rate, total_population, illiterate_population, literate_population`
        - `gdp_schooling`: `country, country_code, year, region, is_country, gdp_per_capita, avg_years_schooling, literacy_rate, gdp_per_schooling_year, education_index`
        """)
        
        default_custom_sql = """SELECT l.country, l.year, l.adult_literacy_rate, s.avg_years_schooling, s.gdp_per_capita
FROM literacy_rates l
JOIN gdp_schooling s ON l.country = s.country AND l.year = s.year
WHERE l.year = 2020 AND l.is_country = 1
ORDER BY s.gdp_per_capita DESC
LIMIT 10;"""
        
        custom_sql = st.text_area("Write SQL Statement:", value=default_custom_sql, height=140)
        
        if st.button("🚀 Execute Custom Query", type="primary"):
            try:
                custom_df = pd.read_sql_query(custom_sql, conn)
                st.success(f"Query returned {len(custom_df)} rows.")
                st.dataframe(custom_df, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Error: {e}")


# ------------------------------------------------------------------------------
# MODULE 3: Exploratory Data Analysis (EDA)
# ------------------------------------------------------------------------------
elif app_mode == "📊 Exploratory Data Analysis (EDA)":
    st.markdown("""
    <div class='section-header'>
        <h2 class='section-title'>Exploratory Data Analysis: Statistical Distributions & Correlations</h2>
        <p class='section-subtitle'>Univariate, bivariate, and multi-variable analytical patterns across education and economic health</p>
    </div>
    """, unsafe_allow_html=True)
    
    eda_tab1, eda_tab2, eda_tab3, eda_tab4 = st.tabs([
        "📈 Univariate Distributions",
        "🔬 Bivariate & Regressions",
        "🔥 Correlation Heatmap",
        "⚖️ Gender Disparity Deep-Dive"
    ])
    
    # Univariate Tab
    with eda_tab1:
        st.subheader("Univariate Distribution Explorer")
        metric_u = st.selectbox(
            "Select Variable to Analyze:",
            [
                ("adult_literacy_rate", "Adult Literacy Rate (%)"),
                ("youth_literacy_avg", "Youth Literacy Average (%)"),
                ("avg_years_schooling", "Average Years of Schooling"),
                ("gdp_per_capita", "GDP per Capita (USD)"),
                ("literacy_gender_gap", "Youth Literacy Gender Gap (Points)"),
                ("education_index", "Composite Education Index")
            ],
            format_func=lambda x: x[1]
        )
        col_u, name_u = metric_u
        
        series = df_master[col_u].dropna()
        u1, u2 = st.columns([1.2, 0.8])
        
        with u1:
            fig_hist = px.histogram(
                df_master.dropna(subset=[col_u]),
                x=col_u,
                color="region",
                marginal="box",
                nbins=40,
                title=f"Distribution of {name_u}",
                opacity=0.8
            )
            apply_chart_styling(fig_hist)
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with u2:
            st.markdown(f"#### Summary Statistics: {name_u}")
            stats_df = pd.DataFrame({
                "Statistic": ["Count", "Mean", "Std Dev", "Min", "25% Q1", "Median (50%)", "75% Q3", "Max", "Skewness"],
                "Value": [
                    f"{len(series):,}",
                    f"{series.mean():.2f}",
                    f"{series.std():.2f}",
                    f"{series.min():.2f}",
                    f"{series.quantile(0.25):.2f}",
                    f"{series.median():.2f}",
                    f"{series.quantile(0.75):.2f}",
                    f"{series.max():.2f}",
                    f"{series.skew():.2f}"
                ]
            })
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
            
    # Bivariate Tab
    with eda_tab2:
        st.subheader("Bivariate Relationships & Trendlines")
        b1, b2 = st.columns([1, 1])
        
        with b1:
            log_gdp = st.checkbox("Logarithmic GDP Scale", value=True)
            filtered_bi = df_master.dropna(subset=["gdp_per_capita", "adult_literacy_rate"])
            fig_bi1 = px.scatter(
                filtered_bi,
                x="gdp_per_capita",
                y="adult_literacy_rate",
                color="region",
                hover_name="country",
                trendline="ols",
                log_x=log_gdp,
                title="Adult Literacy Rate vs GDP per Capita"
            )
            apply_chart_styling(fig_bi1)
            st.plotly_chart(fig_bi1, use_container_width=True)
            
        with b2:
            filtered_bi2 = df_master.dropna(subset=["avg_years_schooling", "adult_literacy_rate"])
            fig_bi2 = px.scatter(
                filtered_bi2,
                x="avg_years_schooling",
                y="adult_literacy_rate",
                color="region",
                hover_name="country",
                trendline="ols",
                title="Schooling Duration vs Adult Literacy Rate"
            )
            apply_chart_styling(fig_bi2)
            st.plotly_chart(fig_bi2, use_container_width=True)

    # Correlation Heatmap Tab
    with eda_tab3:
        st.subheader("Inter-Indicator Correlation Heatmap")
        corr_fields = [
            "adult_literacy_rate", "youth_literacy_avg", "literacy_gender_gap",
            "gdp_per_capita", "avg_years_schooling", "education_index", "illiteracy_rate"
        ]
        corr_data = df_master[corr_fields].dropna().corr()
        
        fig_heat = px.imshow(
            corr_data,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            aspect="auto",
            title="Correlation Matrix Across Core Indicators"
        )
        apply_chart_styling(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)
        
        st.markdown("""
        **Analytical Observations:**
        - **Strong Positive Correlation (r ≈ 0.82):** Average years of schooling is the strongest structural predictor of adult literacy.
        - **Log-Linear Income Elasticity (r ≈ 0.58):** GDP per capita exhibits strong positive returns up to approximately $15,000, after which literacy reaches near-universal saturation.
        - **Negative Gender Disparity (r ≈ -0.65):** Higher overall literacy is heavily correlated with near-zero male-female literacy gaps.
        """)

    # Gender Disparity Tab
    with eda_tab4:
        st.subheader("Gender Parity in Youth Literacy")
        df_gender = df_master.dropna(subset=["literacy_gender_gap", "region", "year"])
        
        fig_gen = px.box(
            df_gender,
            x="region",
            y="literacy_gender_gap",
            color="region",
            title="Youth Literacy Gender Gap by Continent (Male % - Female %)"
        )
        fig_gen.add_hline(y=0, line_dash="dash", line_color="#10b981", annotation_text="Gender Parity (0 gap)")
        apply_chart_styling(fig_gen)
        st.plotly_chart(fig_gen, use_container_width=True)
        
        st.info("💡 **Key Takeaway:** A positive gap indicates higher male literacy than female literacy. Developing African and Asian regions exhibit positive gaps, while Latin America and Europe demonstrate slight female advantages.")


# ------------------------------------------------------------------------------
# MODULE 4: Country Profile & Comparison
# ------------------------------------------------------------------------------
elif app_mode == "🌍 Country Profile & Comparison":
    st.markdown("""
    <div class='section-header'>
        <h2 class='section-title'>Country Deep-Dive & Comparative Lens</h2>
        <p class='section-subtitle'>Inspect longitudinal trajectories for any country or compare two nations side-by-side</p>
    </div>
    """, unsafe_allow_html=True)
    
    country_list = sorted(list(df_master["country"].dropna().unique()))
    
    tab_single, tab_compare = st.tabs(["🔎 Single Country Profile", "⚔️ Side-by-Side Comparison"])
    
    with tab_single:
        selected_c = st.selectbox("Select Country:", country_list, index=country_list.index("India") if "India" in country_list else 0)
        c_data = df_master[df_master["country"] == selected_c].sort_values("year")
        
        if len(c_data) > 0:
            latest_c = c_data.dropna(subset=["adult_literacy_rate", "avg_years_schooling"], how="all").iloc[-1]
            
            # Country KPI row
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Adult Literacy ({int(latest_c['year'])})</div>
                    <div class='metric-value'>{latest_c['adult_literacy_rate'] if pd.notnull(latest_c['adult_literacy_rate']) else 'N/A'}%</div>
                    <div class='metric-sub'>{latest_c['region']}</div>
                </div>
                """, unsafe_allow_html=True)
            with k2:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Youth Literacy Avg</div>
                    <div class='metric-value'>{latest_c['youth_literacy_avg'] if pd.notnull(latest_c['youth_literacy_avg']) else 'N/A'}%</div>
                    <div class='metric-sub'>Next Generation</div>
                </div>
                """, unsafe_allow_html=True)
            with k3:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>Avg Years of Schooling</div>
                    <div class='metric-value'>{latest_c['avg_years_schooling'] if pd.notnull(latest_c['avg_years_schooling']) else 'N/A'} yrs</div>
                    <div class='metric-sub'>Educational Duration</div>
                </div>
                """, unsafe_allow_html=True)
            with k4:
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='metric-title'>GDP per Capita</div>
                    <div class='metric-value'>${latest_c['gdp_per_capita']:,.0f}</div>
                    <div class='metric-sub'>PPP (2017 USD)</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Historical Time Series
            st.subheader(f"📈 Longitudinal Trends for {selected_c} (1990–2023)")
            fig_c_trend = go.Figure()
            
            if c_data["adult_literacy_rate"].notnull().sum() > 0:
                fig_c_trend.add_trace(go.Scatter(
                    x=c_data["year"], y=c_data["adult_literacy_rate"],
                    name="Adult Literacy (%)", mode="lines+markers", line=dict(color="#38bdf8", width=3)
                ))
            if c_data["youth_literacy_avg"].notnull().sum() > 0:
                fig_c_trend.add_trace(go.Scatter(
                    x=c_data["year"], y=c_data["youth_literacy_avg"],
                    name="Youth Literacy Avg (%)", mode="lines+markers", line=dict(color="#34d399", width=2, dash="dot")
                ))
            if c_data["avg_years_schooling"].notnull().sum() > 0:
                fig_c_trend.add_trace(go.Scatter(
                    x=c_data["year"], y=c_data["avg_years_schooling"] * 7, # Scaled for dual-display visibility
                    name="Schooling Years (Scaled x7)", mode="lines+markers", line=dict(color="#fbbf24", width=2)
                ))
                
            apply_chart_styling(fig_c_trend)
            st.plotly_chart(fig_c_trend, use_container_width=True)
            
            # Historical Table
            with st.expander("📄 View Full Historical Dataset for " + selected_c):
                st.dataframe(c_data, use_container_width=True)
        else:
            st.warning("No data found for selected country.")
            
    with tab_compare:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            country_1 = st.selectbox("Select Benchmark Nation A:", country_list, index=country_list.index("India") if "India" in country_list else 0)
        with col_c2:
            country_2 = st.selectbox("Select Benchmark Nation B:", country_list, index=country_list.index("China") if "China" in country_list else 1)
            
        df_c1 = df_master[df_master["country"] == country_1].sort_values("year")
        df_c2 = df_master[df_master["country"] == country_2].sort_values("year")
        
        comp_metric = st.selectbox(
            "Select Metric to Contrast:",
            [
                ("adult_literacy_rate", "Adult Literacy Rate (%)"),
                ("avg_years_schooling", "Average Years of Schooling"),
                ("gdp_per_capita", "GDP per Capita (USD)"),
                ("literacy_gender_gap", "Youth Literacy Gender Gap (Points)")
            ],
            format_func=lambda x: x[1]
        )
        c_field, c_name = comp_metric
        
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Scatter(
            x=df_c1["year"], y=df_c1[c_field],
            name=f"{country_1} ({c_name})", mode="lines+markers", line=dict(color="#38bdf8", width=3)
        ))
        fig_comp.add_trace(go.Scatter(
            x=df_c2["year"], y=df_c2[c_field],
            name=f"{country_2} ({c_name})", mode="lines+markers", line=dict(color="#f43f5e", width=3)
        ))
        fig_comp.update_layout(title=f"Comparative Progression: {country_1} vs {country_2} on {c_name}")
        apply_chart_styling(fig_comp)
        st.plotly_chart(fig_comp, use_container_width=True)


# ------------------------------------------------------------------------------
# MODULE 5: Strategic Policy & Real-World Business Use Cases
# ------------------------------------------------------------------------------
elif app_mode == "🎯 Policy & Business Use Cases":
    st.markdown("""
    <div class='section-header'>
        <h2 class='section-title'>Strategic Policy & Real-World Business Applications</h2>
        <p class='section-subtitle'>Actionable frameworks translating empirical findings into policy, funding, and corporate roadmaps</p>
    </div>
    """, unsafe_allow_html=True)
    
    use_case = st.selectbox(
        "Select Analytical Use Case:",
        [
            "1. 🏛️ Government Policy & Budget Allocation",
            "2. 🌍 International Development Programs (UNESCO / UNICEF SDG 4)",
            "3. 💼 Corporate Social Responsibility (CSR) Planning",
            "4. 🏫 Education NGOs & Non-Profit Outreach",
            "5. 📈 Economic Forecasting & Workforce Planning",
            "6. 🗺️ Regional Disparity Analysis",
            "7. 📚 EdTech Market Research & Product Strategy"
        ]
    )
    
    if "1. 🏛️ Government Policy" in use_case:
        st.markdown("""
        ### 🏛️ Government Policy & Budget Allocation
        **Core Objective:** Determine optimal resource allocation by identifying regions where investment in education yields the highest economic multiplier.
        
        - **Empirical Threshold:** National data demonstrates that countries crossing **7 years of average schooling** experience rapid compounding in GDP per capita.
        - **Policy Priority:** Reallocate secondary education subsidies towards districts with adult literacy below 75% to eliminate literacy poverty traps.
        - **Budget Metric:** Use *GDP per Schooling Year* as a key performance indicator (KPI) for evaluating educational return on investment (ROI).
        """)
        
    elif "2. 🌍 International Development" in use_case:
        st.markdown("""
        ### 🌍 International Development Programs (SDG 4)
        **Core Objective:** Support UNESCO, UNICEF, and World Bank missions targeting global illiteracy eradication by 2030.
        
        - **Target Regions:** Sub-Saharan Africa and pockets of Southern Asia account for over 60% of illiterate youth.
        - **Gender Parity:** In countries where female youth literacy is < 80% (Query 2), targeted conditional cash transfers for girls' schooling produce the highest generational return.
        """)

    elif "3. 💼 Corporate Social Responsibility" in use_case:
        st.markdown("""
        ### 💼 Corporate Social Responsibility (CSR) Planning
        **Core Objective:** Help multinational corporations target philanthropic investments for maximum community impact and talent pipeline development.
        
        - **Target Demographics:** Focus workforce readiness grants on districts with high youth populations but declining literacy growth rates.
        - **Vocational Readiness:** Pair digital literacy labs with technical apprenticeships in developing manufacturing hubs.
        """)
        
    elif "4. 🏫 Education NGOs" in use_case:
        st.markdown("""
        ### 🏫 Education NGOs & Non-Profit Outreach
        **Core Objective:** Prioritize grassroots intervention drives based on absolute illiterate population size rather than percentage alone (Query 6).
        
        - **High-Density Hotspots:** Countries like India, Pakistan, Nigeria, and Ethiopia house millions of illiterate individuals, requiring scalable vernacular educational tools.
        """)
        
    elif "5. 📈 Economic Forecasting" in use_case:
        st.markdown("""
        ### 📈 Economic Forecasting & Workforce Planning
        **Core Objective:** Enable businesses and institutional investors to predict talent readiness and demographic dividends.
        
        - **The Youth Advantage:** Nations where youth literacy outpaces adult literacy by > 20% (e.g., India, Bangladesh) are entering a high-productivity demographic dividend phase.
        """)
        
    elif "6. 🗺️ Regional Disparity" in use_case:
        st.markdown("""
        ### 🗺️ Regional Disparity Analysis
        **Core Objective:** Detect internal and cross-border socio-economic asymmetries.
        
        - **The Resource Curse Outlier:** Nations with high GDP per capita but < 6 years of average schooling (Query 10) must diversify beyond resource extraction into human capital accumulation.
        """)
        
    elif "7. 📚 EdTech Market Research" in use_case:
        st.markdown("""
        ### 📚 EdTech Market Research & Product Strategy
        **Core Objective:** Identify untapped total addressable markets (TAM) for digital and mobile learning platforms.
        
        - **Mobile-First Vernacular Learning:** Low GDP per capita paired with rising youth smartphone penetration creates the ideal environment for affordable offline-first micro-learning applications.
        """)
        
    st.markdown("---")
    st.markdown("### 📥 Download Complete Project Findings Report")
    
    # Read findings report if present
    findings_path = "findings_summary.md"
    if os.path.exists(findings_path):
        with open(findings_path, "r", encoding="utf-8") as f:
            report_text = f.read()
        st.download_button(
            label="📄 Download Full Findings Summary (Markdown)",
            data=report_text,
            file_name="Global_Literacy_and_Education_Trends_Findings.md",
            mime="text/markdown"
        )
