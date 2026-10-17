-- ==============================================================================
-- Global Literacy & Education Trends: An Analytical Study
-- Database Schema: literacy_rates, illiteracy_population, gdp_schooling
-- Compatible with SQLite and MySQL / PostgreSQL
-- ==============================================================================

-- 1. Table: literacy_rates
-- Stores adult and youth literacy rates, gender breakdown, and engineered growth metrics.
DROP TABLE IF EXISTS literacy_rates;
CREATE TABLE literacy_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(10),
    year INTEGER NOT NULL,
    region VARCHAR(50),
    is_country INTEGER DEFAULT 1,
    adult_literacy_rate REAL,
    youth_literacy_male REAL,
    youth_literacy_female REAL,
    youth_literacy_avg REAL,
    literacy_gender_gap REAL,
    literacy_growth_rate REAL
);

CREATE INDEX idx_lit_country_year ON literacy_rates(country, year);
CREATE INDEX idx_lit_region ON literacy_rates(region);
CREATE INDEX idx_lit_is_country ON literacy_rates(is_country);


-- 2. Table: illiteracy_population
-- Stores literacy vs illiteracy rates, total population, and estimated absolute counts.
DROP TABLE IF EXISTS illiteracy_population;
CREATE TABLE illiteracy_population (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(10),
    year INTEGER NOT NULL,
    region VARCHAR(50),
    is_country INTEGER DEFAULT 1,
    literacy_rate REAL,
    illiteracy_rate REAL,
    total_population REAL,
    illiterate_population REAL,
    literate_population REAL
);

CREATE INDEX idx_illit_country_year ON illiteracy_population(country, year);
CREATE INDEX idx_illit_region ON illiteracy_population(region);
CREATE INDEX idx_illit_is_country ON illiteracy_population(is_country);


-- 3. Table: gdp_schooling
-- Stores economic indicators (GDP per capita) paired with average schooling years and composite education indices.
DROP TABLE IF EXISTS gdp_schooling;
CREATE TABLE gdp_schooling (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country VARCHAR(100) NOT NULL,
    country_code VARCHAR(10),
    year INTEGER NOT NULL,
    region VARCHAR(50),
    is_country INTEGER DEFAULT 1,
    gdp_per_capita REAL,
    avg_years_schooling REAL,
    literacy_rate REAL,
    gdp_per_schooling_year REAL,
    education_index REAL
);

CREATE INDEX idx_gdp_country_year ON gdp_schooling(country, year);
CREATE INDEX idx_gdp_region ON gdp_schooling(region);
CREATE INDEX idx_gdp_is_country ON gdp_schooling(is_country);
