"""
Data Preparation, Cleaning, Feature Engineering and SQLite Database Population Pipeline
for Global Literacy & Education Trends: An Analytical Study.
"""

import os
import sqlite3
import numpy as np
import pandas as pd

def run_pipeline():
    print("=" * 70)
    print("Starting Data Preparation & Database Setup Pipeline")
    print("=" * 70)

    # 1. Load Raw Datasets
    raw_dir = "data/raw"
    cleaned_dir = "data/cleaned"
    db_dir = "database"
    os.makedirs(cleaned_dir, exist_ok=True)
    os.makedirs(db_dir, exist_ok=True)

    print("\n[Step 1] Loading raw CSV datasets...")
    df_adult_raw = pd.read_csv(os.path.join(raw_dir, "adult_literacy.csv"))
    df_youth_raw = pd.read_csv(os.path.join(raw_dir, "youth_literacy.csv"))
    df_illit_raw = pd.read_csv(os.path.join(raw_dir, "illiterate_population.csv"))
    df_gdp_raw = pd.read_csv(os.path.join(raw_dir, "gdp_per_capita.csv"))
    df_school_raw = pd.read_csv(os.path.join(raw_dir, "years_schooling.csv"))
    df_pop_raw = pd.read_csv(os.path.join(raw_dir, "population.csv"))

    print(f"  - Adult Literacy: {df_adult_raw.shape}")
    print(f"  - Youth Literacy: {df_youth_raw.shape}")
    print(f"  - Illiterate Population: {df_illit_raw.shape}")
    print(f"  - GDP per Capita: {df_gdp_raw.shape}")
    print(f"  - Years Schooling: {df_school_raw.shape}")
    print(f"  - Population: {df_pop_raw.shape}")

    # Build Region Lookup Map (Country -> OWID Region)
    reg_map = {}
    for df in [df_gdp_raw, df_school_raw, df_youth_raw]:
        if "owid_region" in df.columns:
            for _, row in df.dropna(subset=["owid_region"]).iterrows():
                if row["entity"] not in reg_map:
                    reg_map[row["entity"]] = row["owid_region"]

    # Manual fills for common countries if needed
    fallback_regions = {
        "World": "Global",
        "United States": "North America",
        "United Kingdom": "Europe",
        "India": "Asia",
        "China": "Asia",
        "Brazil": "South America",
        "Australia": "Oceania",
        "Nigeria": "Africa",
        "South Africa": "Africa",
        "Russian Federation": "Europe",
        "Russia": "Europe"
    }
    for k, v in fallback_regions.items():
        if k not in reg_map:
            reg_map[k] = v

    # Helper function to classify countries vs regional aggregates
    def is_country_code(code):
        if not isinstance(code, str):
            return 0
        code = code.strip()
        if len(code) == 3 and not code.startswith("OWID"):
            return 1
        return 0

    print("\n[Step 2] Cleaning and Merging Datasets...")

    # -------------------------------------------------------------
    # 1. df_literacy (Adult & Youth Literacy Rates)
    # -------------------------------------------------------------
    # Adult literacy columns: entity, code, year, adult_literacy_rate__...
    col_adult_rate = [c for c in df_adult_raw.columns if "adult_literacy_rate" in c or "both_sexes" in c][0]
    df_adult_c = df_adult_raw.rename(columns={
        "entity": "country",
        "code": "country_code",
        col_adult_rate: "adult_literacy_rate"
    })[["country", "country_code", "year", "adult_literacy_rate"]].drop_duplicates()

    # Youth literacy columns: entity, code, year, youth_literacy_male, youth_literacy_female
    col_youth_m = [c for c in df_youth_raw.columns if "male" in c and "female" not in c][0]
    col_youth_f = [c for c in df_youth_raw.columns if "female" in c][0]
    df_youth_c = df_youth_raw.rename(columns={
        "entity": "country",
        "code": "country_code",
        col_youth_m: "youth_literacy_male",
        col_youth_f: "youth_literacy_female"
    })[["country", "country_code", "year", "youth_literacy_male", "youth_literacy_female"]].drop_duplicates()

    df_literacy = pd.merge(df_adult_c, df_youth_c, on=["country", "country_code", "year"], how="outer")
    df_literacy["region"] = df_literacy["country"].map(reg_map)
    df_literacy["is_country"] = df_literacy["country_code"].apply(is_country_code)

    # Feature Engineering for df_literacy
    # a. Youth Literacy Average
    df_literacy["youth_literacy_avg"] = (df_literacy["youth_literacy_male"] + df_literacy["youth_literacy_female"]) / 2.0
    # b. Literacy Gender Gap (Male - Female)
    df_literacy["literacy_gender_gap"] = df_literacy["youth_literacy_male"] - df_literacy["youth_literacy_female"]
    # c. Literacy Growth Rate (Year-over-Year improvement per country)
    df_literacy = df_literacy.sort_values(["country", "year"]).reset_index(drop=True)
    df_literacy["prev_rate"] = df_literacy.groupby("country")["adult_literacy_rate"].shift(1)
    df_literacy["prev_year"] = df_literacy.groupby("country")["year"].shift(1)
    yr_diff = df_literacy["year"] - df_literacy["prev_year"]
    df_literacy["literacy_growth_rate"] = np.where(
        yr_diff > 0,
        (df_literacy["adult_literacy_rate"] - df_literacy["prev_rate"]) / yr_diff,
        np.nan
    )
    df_literacy.drop(columns=["prev_rate", "prev_year"], inplace=True)

    # Filter years 1990 - 2023
    df_literacy = df_literacy[(df_literacy["year"] >= 1990) & (df_literacy["year"] <= 2023)].copy()

    # -------------------------------------------------------------
    # 2. df_illiteracy (Illiterate Population Data)
    # -------------------------------------------------------------
    # raw: entity, code, year, illiteracy_rate, literacy_rate
    df_illit_c = df_illit_raw.rename(columns={
        "entity": "country",
        "code": "country_code"
    })[["country", "country_code", "year", "illiteracy_rate", "literacy_rate"]].drop_duplicates()

    # population: entity, code, year, population_historical
    df_pop_c = df_pop_raw.rename(columns={
        "entity": "country",
        "code": "country_code",
        "population_historical": "total_population"
    })[["country", "country_code", "year", "total_population"]].drop_duplicates()

    df_illiteracy = pd.merge(df_illit_c, df_pop_c, on=["country", "country_code", "year"], how="left")
    df_illiteracy["region"] = df_illiteracy["country"].map(reg_map)
    df_illiteracy["is_country"] = df_illiteracy["country_code"].apply(is_country_code)

    # Feature Engineering for df_illiteracy
    # a. Illiteracy % is already illiteracy_rate (explicitly ensure standard column name illiteracy_rate)
    # b. Absolute illiterate & literate population counts
    df_illiteracy["illiterate_population"] = df_illiteracy["total_population"] * (df_illiteracy["illiteracy_rate"] / 100.0)
    df_illiteracy["literate_population"] = df_illiteracy["total_population"] * (df_illiteracy["literacy_rate"] / 100.0)

    # Filter years 1990 - 2023
    df_illiteracy = df_illiteracy[(df_illiteracy["year"] >= 1990) & (df_illiteracy["year"] <= 2023)].copy()

    # -------------------------------------------------------------
    # 3. df_gdp_schooling (GDP & Years of Schooling)
    # -------------------------------------------------------------
    # gdp raw: entity, code, year, ny_gdp_pcap_pp_kd
    df_gdp_c = df_gdp_raw.rename(columns={
        "entity": "country",
        "code": "country_code",
        "ny_gdp_pcap_pp_kd": "gdp_per_capita"
    })[["country", "country_code", "year", "gdp_per_capita"]].drop_duplicates()

    # schooling raw: entity, code, year, literacy_rate, mf_youth_and_adults__15_64_years__average_years_of_education
    col_school = [c for c in df_school_raw.columns if "average_years_of_education" in c or "schooling" in c][0]
    df_school_c = df_school_raw.rename(columns={
        "entity": "country",
        "code": "country_code",
        col_school: "avg_years_schooling"
    })[["country", "country_code", "year", "avg_years_schooling", "literacy_rate"]].drop_duplicates()

    df_gdp_schooling = pd.merge(df_gdp_c, df_school_c, on=["country", "country_code", "year"], how="outer")
    df_gdp_schooling["region"] = df_gdp_schooling["country"].map(reg_map)
    df_gdp_schooling["is_country"] = df_gdp_schooling["country_code"].apply(is_country_code)

    # Feature Engineering for df_gdp_schooling
    # a. GDP per Schooling Year: economic output per year of education
    df_gdp_schooling["gdp_per_schooling_year"] = np.where(
        (df_gdp_schooling["avg_years_schooling"] > 0) & (df_gdp_schooling["gdp_per_capita"].notnull()),
        df_gdp_schooling["gdp_per_capita"] / df_gdp_schooling["avg_years_schooling"],
        np.nan
    )
    # b. Education Index: Composite index (0 to 100) combining access (literacy) and duration (schooling)
    # Standard formula: 50% literacy rate + 50% schooling duration (scaled against 15 years max expected schooling)
    df_gdp_schooling["education_index"] = np.where(
        df_gdp_schooling["literacy_rate"].notnull() & df_gdp_schooling["avg_years_schooling"].notnull(),
        (df_gdp_schooling["literacy_rate"] * 0.5) + (np.clip(df_gdp_schooling["avg_years_schooling"] / 15.0, 0, 1.0) * 50.0),
        np.nan
    )

    # Filter years 1990 - 2023
    df_gdp_schooling = df_gdp_schooling[(df_gdp_schooling["year"] >= 1990) & (df_gdp_schooling["year"] <= 2023)].copy()

    # Reorder columns neatly
    df_literacy = df_literacy[[
        "country", "country_code", "year", "region", "is_country",
        "adult_literacy_rate", "youth_literacy_male", "youth_literacy_female",
        "youth_literacy_avg", "literacy_gender_gap", "literacy_growth_rate"
    ]].sort_values(["country", "year"]).reset_index(drop=True)

    df_illiteracy = df_illiteracy[[
        "country", "country_code", "year", "region", "is_country",
        "literacy_rate", "illiteracy_rate", "total_population",
        "illiterate_population", "literate_population"
    ]].sort_values(["country", "year"]).reset_index(drop=True)

    df_gdp_schooling = df_gdp_schooling[[
        "country", "country_code", "year", "region", "is_country",
        "gdp_per_capita", "avg_years_schooling", "literacy_rate",
        "gdp_per_schooling_year", "education_index"
    ]].sort_values(["country", "year"]).reset_index(drop=True)

    # Round numeric columns for cleanliness
    for col in ["adult_literacy_rate", "youth_literacy_male", "youth_literacy_female", "youth_literacy_avg", "literacy_gender_gap", "literacy_growth_rate"]:
        df_literacy[col] = df_literacy[col].round(4)

    for col in ["literacy_rate", "illiteracy_rate", "illiterate_population", "literate_population"]:
        df_illiteracy[col] = df_illiteracy[col].round(2)

    for col in ["gdp_per_capita", "avg_years_schooling", "literacy_rate", "gdp_per_schooling_year", "education_index"]:
        df_gdp_schooling[col] = df_gdp_schooling[col].round(4)

    print("\n[Step 3] Saving Cleaned Datasets to CSV...")
    df_literacy.to_csv(os.path.join(cleaned_dir, "cleaned_df_literacy.csv"), index=False)
    df_illiteracy.to_csv(os.path.join(cleaned_dir, "cleaned_df_illiteracy.csv"), index=False)
    df_gdp_schooling.to_csv(os.path.join(cleaned_dir, "cleaned_df_gdp_schooling.csv"), index=False)
    print(f"  [OK] Saved cleaned_df_literacy.csv: {df_literacy.shape}")
    print(f"  [OK] Saved cleaned_df_illiteracy.csv: {df_illiteracy.shape}")
    print(f"  [OK] Saved cleaned_df_gdp_schooling.csv: {df_gdp_schooling.shape}")

    print("\n[Step 4] Storing in SQLite Database (education_analytics.db)...")
    db_path = os.path.join(db_dir, "education_analytics.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables with explicit schemas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS literacy_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        country_code TEXT,
        year INTEGER NOT NULL,
        region TEXT,
        is_country INTEGER DEFAULT 1,
        adult_literacy_rate REAL,
        youth_literacy_male REAL,
        youth_literacy_female REAL,
        youth_literacy_avg REAL,
        literacy_gender_gap REAL,
        literacy_growth_rate REAL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS illiteracy_population (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        country_code TEXT,
        year INTEGER NOT NULL,
        region TEXT,
        is_country INTEGER DEFAULT 1,
        literacy_rate REAL,
        illiteracy_rate REAL,
        total_population REAL,
        illiterate_population REAL,
        literate_population REAL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gdp_schooling (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        country_code TEXT,
        year INTEGER NOT NULL,
        region TEXT,
        is_country INTEGER DEFAULT 1,
        gdp_per_capita REAL,
        avg_years_schooling REAL,
        literacy_rate REAL,
        gdp_per_schooling_year REAL,
        education_index REAL
    );
    """)

    # Insert DataFrames into SQLite tables
    df_literacy.to_sql("literacy_rates", conn, if_exists="append", index=False)
    df_illiteracy.to_sql("illiteracy_population", conn, if_exists="append", index=False)
    df_gdp_schooling.to_sql("gdp_schooling", conn, if_exists="append", index=False)

    # Create indexes for high query performance
    cursor.execute("CREATE INDEX idx_lit_country_year ON literacy_rates(country, year);")
    cursor.execute("CREATE INDEX idx_illit_country_year ON illiteracy_population(country, year);")
    cursor.execute("CREATE INDEX idx_gdp_country_year ON gdp_schooling(country, year);")
    conn.commit()
    print("  [OK] Database tables created and populated successfully with indexes.")

    print("\n[Step 5] Validating All 13 Mandatory SQL Queries...")

    queries = [
        ("Query 1: Top 5 countries with highest adult literacy in 2020",
         """
         SELECT country, country_code, region, adult_literacy_rate
         FROM literacy_rates
         WHERE year = 2020 AND is_country = 1 AND adult_literacy_rate IS NOT NULL
         ORDER BY adult_literacy_rate DESC
         LIMIT 5;
         """),

        ("Query 2: Countries where female youth literacy < 80%",
         """
         SELECT DISTINCT country, country_code, region, year, youth_literacy_female
         FROM literacy_rates
         WHERE is_country = 1 AND youth_literacy_female < 80 AND youth_literacy_female IS NOT NULL
         ORDER BY youth_literacy_female ASC
         LIMIT 10;
         """),

        ("Query 3: Average adult literacy per continent (owid region)",
         """
         SELECT region, ROUND(AVG(adult_literacy_rate), 2) AS avg_adult_literacy, COUNT(*) AS data_points
         FROM literacy_rates
         WHERE region IS NOT NULL AND region != 'Global' AND adult_literacy_rate IS NOT NULL
         GROUP BY region
         ORDER BY avg_adult_literacy DESC;
         """),

        ("Query 4: Countries with illiteracy % > 20% in 2000",
         """
         SELECT country, country_code, region, illiteracy_rate AS illiteracy_percentage
         FROM illiteracy_population
         WHERE year = 2000 AND is_country = 1 AND illiteracy_rate > 20
         ORDER BY illiteracy_percentage DESC
         LIMIT 10;
         """),

        ("Query 5: Trend of illiteracy % for India (2000-2020)",
         """
         SELECT country, year, illiteracy_rate, literacy_rate
         FROM illiteracy_population
         WHERE country = 'India' AND year BETWEEN 2000 AND 2020
         ORDER BY year ASC;
         """),

        ("Query 6: Top 10 countries with largest illiterate population in the last year",
         """
         WITH latest_year AS (
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
         LIMIT 10;
         """),

        ("Query 7: Countries with avg_years_schooling > 7 and gdp_per_capita < 5000",
         """
         SELECT DISTINCT country, country_code, region, year,
                ROUND(avg_years_schooling, 2) AS avg_years_schooling,
                ROUND(gdp_per_capita, 2) AS gdp_per_capita
         FROM gdp_schooling
         WHERE is_country = 1 AND avg_years_schooling > 7 AND gdp_per_capita < 5000
         ORDER BY gdp_per_capita ASC
         LIMIT 10;
         """),

        ("Query 8: Rank countries by GDP per schooling for the year 2020",
         """
         SELECT country, country_code, region,
                ROUND(gdp_per_capita, 2) AS gdp_per_capita,
                ROUND(avg_years_schooling, 2) AS avg_years_schooling,
                ROUND(gdp_per_schooling_year, 2) AS gdp_per_schooling_year,
                DENSE_RANK() OVER (ORDER BY gdp_per_schooling_year DESC) AS gdp_schooling_rank
         FROM gdp_schooling
         WHERE year = 2020 AND is_country = 1 AND gdp_per_schooling_year IS NOT NULL
         ORDER BY gdp_schooling_rank ASC
         LIMIT 10;
         """),

        ("Query 9: Find global average schooling years per year",
         """
         SELECT year, ROUND(AVG(avg_years_schooling), 2) AS global_avg_schooling_years, COUNT(country) AS countries_count
         FROM gdp_schooling
         WHERE is_country = 1 AND avg_years_schooling IS NOT NULL
         GROUP BY year
         ORDER BY year DESC
         LIMIT 15;
         """),

        ("Query 10: Top 10 countries in 2020 with highest GDP per capita but lowest schooling (< 6 years)",
         """
         SELECT country, country_code, region,
                ROUND(gdp_per_capita, 2) AS gdp_per_capita,
                ROUND(avg_years_schooling, 2) AS avg_years_schooling
         FROM gdp_schooling
         WHERE year = 2020 AND is_country = 1 AND avg_years_schooling < 6 AND gdp_per_capita IS NOT NULL
         ORDER BY gdp_per_capita DESC
         LIMIT 10;
         """),

        ("Query 11: Countries where illiterate population is high (> 500,000) despite having > 10 avg years of schooling",
         """
         SELECT p.country, p.country_code, p.year,
                CAST(p.illiterate_population AS BIGINT) AS illiterate_population,
                ROUND(p.illiteracy_rate, 2) AS illiteracy_rate,
                ROUND(s.avg_years_schooling, 2) AS avg_years_schooling
         FROM illiteracy_population p
         JOIN gdp_schooling s ON p.country = s.country AND p.year = s.year
         WHERE p.is_country = 1 AND s.avg_years_schooling > 10 AND p.illiterate_population > 500000
         ORDER BY p.illiterate_population DESC
         LIMIT 10;
         """),

        ("Query 12: Compare literacy rates and GDP per capita growth for India over last 20 years (2000-2020)",
         """
         SELECT l.country, l.year,
                l.adult_literacy_rate,
                l.youth_literacy_avg,
                ROUND(g.gdp_per_capita, 2) AS gdp_per_capita
         FROM literacy_rates l
         JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
         WHERE l.country = 'India' AND l.year BETWEEN 2000 AND 2020
         ORDER BY l.year ASC;
         """),

        ("Query 13: Difference between youth male and female rates for countries with GDP per capita > $30,000 in 2020",
         """
         SELECT l.country, l.country_code, l.year,
                ROUND(g.gdp_per_capita, 2) AS gdp_per_capita,
                l.youth_literacy_male,
                l.youth_literacy_female,
                ROUND(l.literacy_gender_gap, 2) AS youth_literacy_gender_gap
         FROM literacy_rates l
         JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
         WHERE l.year = 2020 AND l.is_country = 1 AND g.gdp_per_capita > 30000 
           AND l.youth_literacy_male IS NOT NULL AND l.youth_literacy_female IS NOT NULL
         ORDER BY g.gdp_per_capita DESC
         LIMIT 10;
         """)
    ]

    for title, q in queries:
        print(f"\n---> {title}")
        res = pd.read_sql_query(q, conn)
        print(res.to_string(index=False))

    conn.close()
    print("\n" + "=" * 70)
    print("Pipeline Execution Completed Successfully!")
    print("=" * 70)

if __name__ == "__main__":
    run_pipeline()
