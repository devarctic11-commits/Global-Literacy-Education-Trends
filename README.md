# 📊 Global Literacy & Education Trends: An Analytical Study

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red.svg)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end data analytics and engineering project investigating global adult literacy, youth literacy, illiteracy demographics, GDP per capita, and average years of schooling across countries and years (1990–2023).

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Domain & Business Use Cases](#-domain--business-use-cases)
3. [Architecture & Folder Structure](#-architecture--folder-structure)
4. [Datasets & Data Ingestion](#-datasets--data-ingestion)
5. [Data Cleaning & Feature Engineering](#-data-cleaning--feature-engineering)
6. [SQL Database Design & 13 Core Queries](#-sql-database-design--13-core-queries)
7. [Streamlit Interactive Application](#-streamlit-interactive-application)
8. [Jupyter Notebook (EDA & Modeling)](#-jupyter-notebook-eda--modeling)
9. [How to Run the Project](#-how-to-run-the-project)
10. [Key Analytical Findings](#-key-analytical-findings)

---

## 🎯 Project Overview
Literacy rates are a fundamental measure of human development, economic potential, and equitable social outreach. This project analyzes historical indicators from **Our World in Data (OWID)**, the **World Bank**, and **UNESCO** to uncover global patterns, education-to-income correlations, and regional disparities.

### Key Objectives:
- Extract, clean, and merge multi-indicator datasets from 1990 to 2023.
- Engineer domain-specific metrics (Education Index, Gender Disparity Gaps, GDP per Schooling Year).
- Design a relational SQL schema with 3 core tables and execute 13 business queries.
- Develop a production-grade **Streamlit Dashboard** featuring an interactive SQL query runner, EDA visualizations, world choropleth maps, and country profile analyzers.

---

## 💼 Domain & Business Use Cases
1. **🏛️ Government Policy & Budget Allocation:** Identify regional education-to-GDP returns to optimize national funding.
2. **🌍 International Development Programs (UNESCO SDG 4):** Direct global literacy funds to high-illiteracy clusters.
3. **💼 Corporate Social Responsibility (CSR) Planning:** Target corporate community initiatives to boost workforce readiness.
4. **🏫 Education NGOs & Non-Profits:** Prioritize literacy campaigns based on absolute illiterate population sizes.
5. **📈 Economic Forecasting & Workforce Planning:** Predict talent availability and demographic dividend realization.
6. **🗺️ Regional Disparity Analysis:** Detect resource-curse economies with high income but low educational schooling.
7. **📚 EdTech Market Research:** Identify emerging geographic markets for affordable mobile learning solutions.

---

## 🏗️ Architecture & Folder Structure

```text
Global Literacy & Education Trends/
├── data/
│   ├── raw/                                  # Raw CSV files downloaded from OWID
│   │   ├── adult_literacy.csv
│   │   ├── youth_literacy.csv
│   │   ├── illiterate_population.csv
│   │   ├── gdp_per_capita.csv
│   │   ├── years_schooling.csv
│   │   └── population.csv
│   └── cleaned/                              # Preprocessed & feature-engineered CSVs
│       ├── cleaned_df_literacy.csv
│       ├── cleaned_df_illiteracy.csv
│       └── cleaned_df_gdp_schooling.csv
├── database/
│   ├── education_analytics.db               # SQLite database with indexed tables
│   ├── schema.sql                            # DDL table creation scripts
│   ├── queries.sql                           # 13 capstone SQL queries with documentation
│   └── setup_database.py                     # Database connection & management script
├── notebooks/
│   └── Global_Literacy_and_Education_Trends_EDA.ipynb  # End-to-end Jupyter Notebook
├── scripts/
│   ├── prepare_data.py                       # Automated cleaning, feature engineering & DB population
│   └── build_notebook.py                     # Notebook generation script
├── app.py                                    # Streamlit web application
├── findings_summary.md                       # Comprehensive analytical report & findings
├── requirements.txt                          # Project python dependencies
└── README.md                                 # Complete documentation
```

---

## 📥 Datasets & Data Ingestion
All datasets are sourced directly from [Our World in Data (OWID)](https://ourworldindata.org/grapher/):
1. **Adult Literacy Rate (15+ Years):** `literacy-rate-adults.csv`
2. **Youth Literacy Rate (15–24 Years, Male & Female):** `literacy-rate-of-young-men-and-women.csv`
3. **Illiterate Population (Total & Rate):** `literate-and-illiterate-world-population.csv`
4. **GDP per Capita (PPP constant 2017 USD):** `gdp-per-capita-worldbank.csv`
5. **Average Years of Schooling:** `literacy-rates-vs-average-years-of-schooling.csv`
6. **Historical Total Population:** `population.csv`

---

## ⚙️ Data Cleaning & Feature Engineering

### Cleaning Workflow:
- Filtered records to the standard benchmark range: **1990–2023**.
- Differentiated sovereign nations from regional aggregates using ISO 3-letter codes (`is_country = 1`).
- Imputed geographic continents using regional mappings.
- Cleaned null values and deduplicated observation keys `(country, year)`.

### Engineered Features:
| Feature Name | Formulation | Purpose |
|---|---|---|
| **`Illiteracy %`** | `illiteracy_rate` | Direct percentage of population unable to read/write. |
| **`Literacy Gender Gap`** | `youth_literacy_male - youth_literacy_female` | Quantifies male-female disparity in percentage points. |
| **`Youth Literacy Avg`** | `(youth_literacy_male + youth_literacy_female) / 2` | Single blended metric for youth literacy health. |
| **`GDP per Schooling Year`** | `gdp_per_capita / avg_years_schooling` | Economic productivity generated per year of national education. |
| **`Education Index`** | `0.5 * literacy_rate + 0.5 * (avg_years_schooling / 15 * 100)` | Composite index (0–100) combining access and duration. |
| **`Literacy Growth Rate`** | `(adult_literacy_rate - prev_rate) / year_diff` | Year-over-year rate of adult literacy change. |
| **`Illiterate Population Count`**| `total_population * (illiteracy_rate / 100)` | Absolute number of illiterate individuals in a nation. |

---

## 🧮 SQL Database Design & 13 Core Queries

The SQLite database (`database/education_analytics.db`) contains three structured tables:
1. `literacy_rates`
2. `illiteracy_population`
3. `gdp_schooling`

### 13 Capstone Queries Overview:
1. **Query 1:** Top 5 countries with highest adult literacy in 2020.
2. **Query 2:** Countries where female youth literacy is under 80%.
3. **Query 3:** Average adult literacy per continent.
4. **Query 4:** Countries with illiteracy % > 20% in the year 2000.
5. **Query 5:** India's 20-year illiteracy decline trend (2000–2020).
6. **Query 6:** Top 10 countries with largest absolute illiterate population in the latest year.
7. **Query 7:** High-efficiency nations with schooling > 7 years and GDP per capita < $5,000.
8. **Query 8:** Country ranking by GDP per schooling year for 2020.
9. **Query 9:** Global average schooling progression over time.
10. **Query 10:** Top 10 high-GDP nations with lowest schooling (< 6 years) in 2020.
11. **Query 11:** Nations with large illiterate populations (>500,000) despite > 10 years average schooling.
12. **Query 12:** Longitudinal comparison of literacy vs GDP per capita growth for India.
13. **Query 13:** Youth literacy gender disparity for high-income nations (GDP > $30,000) in 2020.

*All SQL statements and results are available in [`database/queries.sql`](file:///d:/Global%20Literacy%20&%20Education%20Trends/database/queries.sql) and the interactive SQL Studio in the Streamlit app.*

---

## 💻 Streamlit Interactive Application
The application includes 5 comprehensive modules:
1. **🌐 Executive Overview:** Interactive 3D/Choropleth World Map, metric cards, continental boxplots, and longitudinal schooling trends.
2. **🧮 SQL Query Studio:** Run all 13 project queries with one click, inspect live data tables, download CSV outputs, and run arbitrary custom SQL queries in the interactive console.
3. **📊 Exploratory Data Analysis (EDA):** Univariate distributions, bivariate scatter plots with OLS regression lines, correlation heatmaps, and gender gap analysis.
4. **🌍 Country Profile & Comparison:** Deep-dive into historical indicators for any country, or compare two nations side-by-side.
5. **🎯 Policy & Business Use Cases:** Actionable frameworks tailored to Ministries of Education, UNESCO, CSR directors, and EdTech founders.

---

## 🚀 How to Run the Project

### Prerequisites:
- Python 3.10+
- Anaconda / pip

### 1. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the Data Pipeline (Prepares data and populates SQLite DB):
```bash
python scripts/prepare_data.py
```

### 3. Launch the Streamlit Web Application:
```bash
streamlit run app.py
```
*The app will automatically open in your default browser at `http://localhost:8501`.*

### 4. Open the Jupyter Notebook:
```bash
jupyter notebook notebooks/Global_Literacy_and_Education_Trends_EDA.ipynb
```

---

## 🏆 Deliverables Checklist
- [x] **3 Cleaned DataFrames** saved in `data/cleaned/`
- [x] **SQL Scripts** for table creation & data insertion in `database/schema.sql` and `database/setup_database.py`
- [x] **13 Project SQL Queries** tested and documented in `database/queries.sql`
- [x] **Jupyter Notebook** with comprehensive EDA and SQL outputs in `notebooks/`
- [x] **Production Streamlit App** in `app.py`
- [x] **Analytical Findings Summary** in `findings_summary.md`
