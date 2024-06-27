from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from fake_useragent import UserAgent
import pandas as pd
import time
from datetime import datetime

# Setup WebDriver
ua = UserAgent()
user_agent = ua.random
edge_options = webdriver.EdgeOptions()
edge_options.add_argument(f"user-agent={user_agent}")
#edge_options.add_argument("--headless")
edge_options.add_argument("--incognito")

# Disable images
prefs = {"profile.default_content_settings": {"images": 2}}
edge_options.add_experimental_option("prefs", prefs)

driver_service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=driver_service, options=edge_options)
driver.set_page_load_timeout(600)
print("1. Installed driver")

wait = WebDriverWait(driver, 10)  # Increased wait time for robustness

driver.get('https://fie.org/athletes')
wait.until(EC.presence_of_element_located((By.ID, "weaponFoil")))

# Define categories
categories = [
    {"weapon": "weaponFoil", "gender": "genderMen", "level": "levelSenior", "name": "Foil_Men_Senior"},
    {"weapon": "weaponFoil", "gender": "genderWomen", "level": "levelSenior", "name": "Foil_Women_Senior"},
    {"weapon": "weaponEpee", "gender": "genderMen", "level": "levelSenior", "name": "Epee_Men_Senior"},
    {"weapon": "weaponEpee", "gender": "genderWomen", "level": "levelSenior", "name": "Epee_Women_Senior"},
    {"weapon": "weaponSabre", "gender": "genderMen", "level": "levelSenior", "name": "Sabre_Men_Senior"},
    {"weapon": "weaponSabre", "gender": "genderWomen", "level": "levelSenior", "name": "Sabre_Women_Senior"},
    {"weapon": "weaponFoil", "gender": "genderMen", "level": "levelJunior", "name": "Foil_Men_Junior"},
    {"weapon": "weaponFoil", "gender": "genderWomen", "level": "levelJunior", "name": "Foil_Women_Junior"},
    {"weapon": "weaponEpee", "gender": "genderMen", "level": "levelJunior", "name": "Epee_Men_Junior"},
    {"weapon": "weaponEpee", "gender": "genderWomen", "level": "levelJunior", "name": "Epee_Women_Junior"},
    {"weapon": "weaponSabre", "gender": "genderMen", "level": "levelJunior", "name": "Sabre_Men_Junior"},
    {"weapon": "weaponSabre", "gender": "genderWomen", "level": "levelJunior", "name": "Sabre_Women_Junior"}
]

all_data = []

for category in categories:
    driver.get('https://fie.org/athletes')
    wait.until(EC.presence_of_element_located((By.ID, category["weapon"])))
    
    # Select weapon
    weapon_option = driver.find_element(By.ID, category["weapon"])
    driver.execute_script("arguments[0].click();", weapon_option)
    wait.until(EC.presence_of_element_located((By.ID, category["gender"])))
    
    # Select gender
    gender_option = driver.find_element(By.ID, category["gender"])
    driver.execute_script("arguments[0].click();", gender_option)
    wait.until(EC.presence_of_element_located((By.ID, category["level"])))
    
    # Select level
    level_option = driver.find_element(By.ID, category["level"])
    driver.execute_script("arguments[0].click();", level_option)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tr")))

    # Ensure the table data is fully loaded
    table_rows = driver.find_elements(By.CSS_SELECTOR, "table.table tr")
    while not table_rows:
        time.sleep(1)
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table.table tr")
    
    for _ in range(100):
        table_rows = driver.find_elements(By.CSS_SELECTOR, "table.table tr")
        
        data = []  
        for row in table_rows[1:]:  
            cols = row.find_elements(By.TAG_NAME, "td")
            cols_text = [col.text for col in cols]
            data.append(cols_text)
        
        for record in data:
            record.append(category['name'])
        
        all_data.extend(data)
        
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next")
            driver.execute_script("arguments[0].click();", next_button)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table tr")))
        except NoSuchElementException:
            continue

# Define columns
columns = ['Rank', 'Points', 'Name', 'Country', 'Hand', 'Age', 'Category']
df = pd.DataFrame(all_data, columns=columns)

# Add scrape date
scrape_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df['Scrape_Date'] = scrape_date
df['id'] = range(1, len(df) + 1)

# Save to CSV
df.to_csv('Rankings.csv', index=False)

# Print the number of rows, head(10) and tail(10)
print(f"3. Finished web scrape of FIE Points and Rankings. Total rows scraped: {len(df)}")
print("First 10 rows:")
print(df.head(10))
print("Last 10 rows:")
print(df.tail(10))

driver.quit()

