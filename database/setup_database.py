"""
Standalone Database Setup and Query Runner for Global Literacy & Education Trends.
Can create SQLite database directly or connect to MySQL.
"""

import os
import sqlite3
import pandas as pd

def get_connection(db_path="database/education_analytics.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    return conn

def execute_query(sql, db_path="database/education_analytics.db"):
    conn = get_connection(db_path)
    try:
        df = pd.read_sql_query(sql, conn)
        return df
    finally:
        conn.close()

if __name__ == "__main__":
    db_file = os.path.join("database", "education_analytics.db")
    if not os.path.exists(db_file):
        print("Database not found. Running prepare_data.py to build it...")
        import subprocess, sys
        subprocess.run([sys.executable, "scripts/prepare_data.py"], check=True)
    else:
        print(f"Connecting to existing database: {db_file}")
        test_df = execute_query("SELECT COUNT(*) AS total_literacy_records FROM literacy_rates;")
        print(test_df)
        print("Database is fully operational!")
