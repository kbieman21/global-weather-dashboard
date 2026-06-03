

# Scrape weather data from a website using Selenium


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
from datetime import datetime



# ====================== PROJECT ROOT SETUP ======================
# This ensures paths are always relative to the project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)        # Go up one level from scripts/

RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'raw_data')
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# ====================== SETUP ======================
options = Options()
# options.add_argument("--headless")        # this is commented for testing so I can see the browser. After testing, I will uncomment this line to run in headless mode.
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Educational Weather Scraper - Capstone Project)")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Create folders
os.makedirs('raw_data', exist_ok=True)
#os.makedirs('data', exist_ok=True)

# my target is the weather website given in my assignment instructions.
URL = "https://www.timeanddate.com/weather/"  


print("Loading weather page...")
driver.get(URL)
time.sleep(5)   # giving time for the big table to load



# ====================== SCRAPING LOGIC ======================
weather_data = []

# Find all rows in the table body
rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

print(f"Found {len(rows)} rows in the weather table.")

    
   
for row in rows:
    try:
        # Get all <td> cells in this row
        cells = row.find_elements(By.TAG_NAME, "td")
        
        if len(cells) < 3:
            continue

        # City name and link (from <a> tag)
        city_element = cells[0].find_element(By.TAG_NAME, "a")
        city = city_element.text.strip()
        
        # Local Time (usually second column)
        local_time = cells[1].text.strip()
        
        # Temperature (usually fourth column)
        temperature = cells[3].text.strip()
        
        # Weather Condition
        condition = cells[4].text.strip() if len(cells) > 4 else "N/A"

        weather_data.append({
            "City": city,
            "Local_Time": local_time,
            "Temperature": temperature,
            "Condition": condition,
            "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except:
        continue  # Skip problematic rows

# ====================== SAVE DATA ======================
df = pd.DataFrame(weather_data)

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#raw_file = f"./raw_data/weather_raw_{timestamp}.csv"
filename = f"weather_raw_{timestamp}.csv"
filepath = os.path.join(RAW_DATA_DIR, filename)


df.to_csv(filepath, index=False)

print(f"\nScraping completed successfully!")
print(f"Total cities scraped: {len(df)}")
print(f"File saved: {filepath}")

# Show preview
print("\nPreview:")
print(df.head(10))

driver.quit()