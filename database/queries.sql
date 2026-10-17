-- ==============================================================================
-- Global Literacy & Education Trends: An Analytical Study
-- Standard SQL Queries Repository (Queries 1 to 13)
-- Target Database: education_analytics.db
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- PART 1: Queries on literacy_rates
-- ------------------------------------------------------------------------------

-- Query 1: Get top 5 countries with highest adult literacy in 2020.
-- Business Context: Benchmarks top educational performers for standard setting.
SELECT country, country_code, region, adult_literacy_rate
FROM literacy_rates
WHERE year = 2020 AND is_country = 1 AND adult_literacy_rate IS NOT NULL
ORDER BY adult_literacy_rate DESC
LIMIT 5;

-- Query 2: Find countries where female youth literacy < 80%.
-- Business Context: Pinpoints priority regions requiring gender-focused educational initiatives (UNESCO SDG 4).
SELECT DISTINCT country, country_code, region, year, youth_literacy_female
FROM literacy_rates
WHERE is_country = 1 AND youth_literacy_female < 80 AND youth_literacy_female IS NOT NULL
ORDER BY youth_literacy_female ASC;

-- Query 3: Average adult literacy per continent (owid region).
-- Business Context: Enables continental macro-comparisons to direct global development grants.
SELECT region, 
       ROUND(AVG(adult_literacy_rate), 2) AS avg_adult_literacy,
       COUNT(*) AS total_records
FROM literacy_rates
WHERE region IS NOT NULL AND region != 'Global' AND adult_literacy_rate IS NOT NULL
GROUP BY region
ORDER BY avg_adult_literacy DESC;


-- ------------------------------------------------------------------------------
-- PART 2: Queries on illiteracy_population
-- ------------------------------------------------------------------------------

-- Query 4: Countries with illiteracy % > 20% in 2000.
-- Business Context: Establishes a historical baseline at the turn of the millennium for assessing 20-year progress.
SELECT country, country_code, region, illiteracy_rate AS illiteracy_percentage
FROM illiteracy_population
WHERE year = 2000 AND is_country = 1 AND illiteracy_rate > 20
ORDER BY illiteracy_percentage DESC;

-- Query 5: Trend of illiteracy % for India (2000–2020).
-- Business Context: Tracks national education policy success over a 20-year timeframe in one of the world's most populous nations.
SELECT country, year, illiteracy_rate, literacy_rate
FROM illiteracy_population
WHERE country = 'India' AND year BETWEEN 2000 AND 2020
ORDER BY year ASC;

-- Query 6: Top 10 countries with largest illiterate population in the last year.
-- Business Context: Critical for international NGOs and EdTech providers targeting total addressable populations.
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


-- ------------------------------------------------------------------------------
-- PART 3: Queries on gdp_schooling
-- ------------------------------------------------------------------------------

-- Query 7: Find countries with avg_years_schooling > 7 and gdp_per_capita < 5000.
-- Business Context: Identifies high education efficiency / human capital despite low financial resources.
SELECT DISTINCT country, country_code, region, year,
       ROUND(avg_years_schooling, 2) AS avg_years_schooling,
       ROUND(gdp_per_capita, 2) AS gdp_per_capita
FROM gdp_schooling
WHERE is_country = 1 AND avg_years_schooling > 7 AND gdp_per_capita < 5000
ORDER BY gdp_per_capita ASC;

-- Query 8: Rank countries by GDP per schooling for the year 2020.
-- Business Context: Measures economic productivity output generated per year of average education across nations.
SELECT country, country_code, region,
       ROUND(gdp_per_capita, 2) AS gdp_per_capita,
       ROUND(avg_years_schooling, 2) AS avg_years_schooling,
       ROUND(gdp_per_schooling_year, 2) AS gdp_per_schooling_year,
       DENSE_RANK() OVER (ORDER BY gdp_per_schooling_year DESC) AS gdp_schooling_rank
FROM gdp_schooling
WHERE year = 2020 AND is_country = 1 AND gdp_per_schooling_year IS NOT NULL
ORDER BY gdp_schooling_rank ASC;

-- Query 9: Find global average schooling years per year.
-- Business Context: Tracks long-term global progress in schooling duration over multiple decades.
SELECT year, 
       ROUND(AVG(avg_years_schooling), 2) AS global_avg_schooling_years,
       COUNT(country) AS countries_reported
FROM gdp_schooling
WHERE is_country = 1 AND avg_years_schooling IS NOT NULL
GROUP BY year
ORDER BY year DESC;


-- ------------------------------------------------------------------------------
-- PART 4: Join Queries (Multi-Table Integration)
-- ------------------------------------------------------------------------------

-- Query 10: List top 10 countries in 2020 with highest GDP per capita but lowest average years of schooling (less than 6).
-- Business Context: Detects natural-resource-dependent or rentier economies where high income has not translated into schooling duration.
SELECT country, country_code, region,
       ROUND(gdp_per_capita, 2) AS gdp_per_capita,
       ROUND(avg_years_schooling, 2) AS avg_years_schooling
FROM gdp_schooling
WHERE year = 2020 AND is_country = 1 AND avg_years_schooling < 6 AND gdp_per_capita IS NOT NULL
ORDER BY gdp_per_capita DESC
LIMIT 10;

-- Query 11: Show countries where illiterate population is high (> 500,000) despite having > 10 avg years of schooling.
-- Business Context: Reveals systemic disparities or demographic scale effects where high national schooling averages mask pockets of illiteracy.
SELECT p.country, p.country_code, p.year,
       CAST(p.illiterate_population AS BIGINT) AS illiterate_population,
       ROUND(p.illiteracy_rate, 2) AS illiteracy_rate,
       ROUND(s.avg_years_schooling, 2) AS avg_years_schooling
FROM illiteracy_population p
JOIN gdp_schooling s ON p.country = s.country AND p.year = s.year
WHERE p.is_country = 1 AND s.avg_years_schooling > 10 AND p.illiterate_population > 500000
ORDER BY p.illiterate_population DESC;

-- Query 12: Compare literacy rates and GDP per capita growth for a selected country over the last 20 years (India 2000-2020).
-- Business Context: Demonstrates empirical co-movement of educational attainment and national income expansion.
SELECT l.country, l.year,
       l.adult_literacy_rate,
       l.youth_literacy_avg,
       ROUND(g.gdp_per_capita, 2) AS gdp_per_capita
FROM literacy_rates l
JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
WHERE l.country = 'India' AND l.year BETWEEN 2000 AND 2020
ORDER BY l.year ASC;

-- Query 13: Show the difference between youth literacy male and female rates for countries with GDP per capita above $30,000 in 2020.
-- Business Context: Tests the hypothesis of gender convergence in youth literacy in high-income economies.
SELECT l.country, l.country_code, l.year,
       ROUND(g.gdp_per_capita, 2) AS gdp_per_capita,
       l.youth_literacy_male,
       l.youth_literacy_female,
       ROUND(l.literacy_gender_gap, 2) AS youth_literacy_gender_gap
FROM literacy_rates l
JOIN gdp_schooling g ON l.country = g.country AND l.year = g.year
WHERE l.year = 2020 AND l.is_country = 1 AND g.gdp_per_capita > 30000 
  AND l.youth_literacy_male IS NOT NULL AND l.youth_literacy_female IS NOT NULL
ORDER BY g.gdp_per_capita DESC;
