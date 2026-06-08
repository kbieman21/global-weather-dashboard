# Load raw scraped weather data, clean it, and save cleaned version
import pandas as pd
import os
from datetime import datetime

# ====================== CONFIGURATION ======================
# Find project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'raw_data')
CLEAN_DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

os.makedirs(CLEAN_DATA_DIR, exist_ok=True)

# ====================== LOAD LATEST RAW DATA ======================
def load_latest_raw_data():
    #Load the most recent raw CSV file from the raw_data directory
    raw_files = [f for f in os.listdir(RAW_DATA_DIR) if f.startswith('weather_raw_') and f.endswith('.csv')]
    
    if not raw_files:
        raise FileNotFoundError("No raw weather data files found!")
    
    # Get the latest file
    latest_file = max(raw_files, key=lambda x: os.path.getctime(os.path.join(RAW_DATA_DIR, x)))
    filepath = os.path.join(RAW_DATA_DIR, latest_file)
    
    print(f"Loading raw file: {latest_file}")
    df = pd.read_csv(filepath)
    return df, latest_file


# ====================== MAIN CLEANING FUNCTION ======================
def clean_weather_data(df):
    print(f"Original shape: {df.shape} rows × {df.shape[1]} columns")
    
    # Make a copy to avoid warnings
    df_clean = df.copy()
    
    # 1. Remove duplicate rows (if any)
    df_clean = df_clean.drop_duplicates()
    
    # 2. Clean Temperature column (remove non-numeric characters like °C, °F)
    df_clean['Temperature'] = df_clean['Temperature'].astype(str).str.extract('(\d+)').astype(float)
    
    # 3. Handle missing values
    df_clean['Condition'] = df_clean['Condition'].fillna('Unknown')
    
    # 4. Convert Scraped_At to proper datetime
    if 'Scraped_At' in df_clean.columns:
        df_clean['Scraped_At'] = pd.to_datetime(df_clean['Scraped_At'], errors='coerce')
    
    # 5. Add a new useful column: Hemisphere (optional but nice for analysis)
    def get_hemisphere(city):
        southern = ['Sydney', 'Rio de Janeiro', 'Cape Town', 'Buenos Aires']
        return 'Southern' if any(s in city for s in southern) else 'Northern'
    
    df_clean['Hemisphere'] = df_clean['City'].apply(get_hemisphere)
    
    print(f"Cleaned shape: {df_clean.shape} rows × {df_clean.shape[1]} columns")
    
    return df_clean


# ====================== MAIN EXECUTION ======================
if __name__ == "__main__":
    try:
        # Load raw data
        df_raw, filename = load_latest_raw_data()
        
        print("\n" + "="*60)
        print("BEFORE CLEANING (First 5 rows)")
        print("="*60)
        print(df_raw.head())
        
        # Clean the data
        df_clean = clean_weather_data(df_raw)
        
        print("\n" + "="*60)
        print("AFTER CLEANING (First 5 rows)")
        print("="*60)
        print(df_clean.head())
        
        # Save cleaned data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        clean_filename = f"weather_clean_{timestamp}.csv"
        clean_path = os.path.join(CLEAN_DATA_DIR, clean_filename)
        
        df_clean.to_csv(clean_path, index=False)
        
        print(f"\nData cleaning completed successfully!")
        print(f"Cleaned file saved to: {clean_path}")
        
    except Exception as e:
        print(f"Error during cleaning: {e}")