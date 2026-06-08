# Load cleaned weather data and store it in a SQLite database
import os
import sqlite3
import pandas as pd
from datetime import datetime

# ====================== PATH CONFIGURATION ======================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'weather_database.db')

os.makedirs(DATA_DIR, exist_ok=True)

# ====================== LOAD LATEST CLEANED DATA ======================
def load_latest_clean_data():
    # Load the most recent cleaned CSV file
    clean_files = [f for f in os.listdir(DATA_DIR) if f.startswith('weather_clean_') and f.endswith('.csv')]
    
    if not clean_files:
        raise FileNotFoundError("No cleaned weather data files found in 'data/' folder!")
    
    # Get the latest cleaned file
    latest_file = max(clean_files, key=lambda x: os.path.getctime(os.path.join(DATA_DIR, x)))
    filepath = os.path.join(DATA_DIR, latest_file)
    
    print(f"Loading cleaned file: {latest_file}")
    df = pd.read_csv(filepath)
    return df, latest_file


# ====================== CREATE / UPDATE DATABASE ======================
def save_to_sqlite(df):
    # Save DataFrame to SQLite database
    conn = sqlite3.connect(DB_PATH)
    
    # Save to table (if table exists, replace it)
    df.to_sql('weather', conn, if_exists='replace', index=False)
    
    # Create indexes for faster queries (optional but recommended)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_city ON weather(City)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_scraped ON weather(Scraped_At)")
    
    conn.close()
    print(f"Data successfully saved to SQLite database: {DB_PATH}")


# ====================== QUERY FUNCTIONS ======================
def show_sample_data():
    # Show sample data from the database
    conn = sqlite3.connect(DB_PATH)
    
    print("\n" + "="*60)
    print("SAMPLE DATA FROM DATABASE")
    print("="*60)
    
    query = "SELECT * FROM weather ORDER BY Temperature DESC LIMIT 10"
    result = pd.read_sql_query(query, conn)
    print(result)
    
    print(f"\nTotal records in database: {len(pd.read_sql_query('SELECT * FROM weather', conn))}")
    
    conn.close()

# ====================== MAIN EXECUTION ======================
if __name__ == "__main__":
    try:
        # Load cleaned data
        df_clean, filename = load_latest_clean_data()
        
        print(f"\nLoaded {len(df_clean)} records for database insertion.")
        
        # Save to SQLite
        save_to_sqlite(df_clean)
        
        # Show sample
        show_sample_data()
        
        print("\nDatabase setup completed successfully!")
        print(f"Database location: {DB_PATH}")
        
    except Exception as e:
        print(f"Error: {e}")