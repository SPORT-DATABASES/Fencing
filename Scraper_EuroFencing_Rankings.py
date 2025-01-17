import time
import pandas as pd
import os
from io import StringIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.headless = False

## For indivudals, thsi code is only taking the current season and for Cadets

driver = webdriver.Edge(options=options)
driver.get("https://www.eurofencing.info/rankings/individual-rankings")

# Select id of appropriate tag
select_gender = Select(driver.find_element(By.ID,'gender'))
select_weapon = Select(driver.find_element(By.ID,'weapon'))
select_age = Select(driver.find_element(By.ID,'age'))
#select_year = Select(driver.find_element(By.ID,'year'))

options_gender = select_gender.options
options_weapon = select_weapon.options
options_age = select_age.options
#options_year = select_year.options

options_gender_l=[i.text for i in options_gender]
options_weapon_l=[i.text for i in options_weapon]
options_age_l=[i.text for i in options_age[0:1]]
#options_year_l=[i.text for i in options_year[0:5]]

c=[]
table_1_data=[]
table_2_data=[]

for gender in options_gender_l:
    for weapon in options_weapon_l:
        for age in options_age_l:
            #for year in options_year_l:
                # Selecting id of appropriate tag
            select_gender = Select(driver.find_element(By.ID,'gender'))
            select_weapon = Select(driver.find_element(By.ID,'weapon'))
            select_age = Select(driver.find_element(By.ID,'age'))
            select_year = Select(driver.find_element(By.ID,'year'))
            
            select_gender.select_by_visible_text(gender) # select women
            select_weapon.select_by_visible_text(weapon) # select weapon
            select_age.select_by_visible_text(age) # select age
            #select_year.select_by_visible_text(year) # select year
            driver.find_element(By.XPATH, '//*[@id="print-rankings"]/div/form/div/div[6]/div/input').click()

            table_html = driver.find_element(By.TAG_NAME,'html').get_attribute('innerHTML')
                            
            table_2 = pd.read_html(StringIO(table_html))[1]
            table_2['Gender']=gender
            table_2['Weapon']=weapon
            table_2['Age']=age
            #table_2['Year']=year
            #print(f" Scraping table_2 for {gender}, {weapon}, {age}")
            table_2_data.append(table_2)
            
            driver.implicitly_wait(10)    


table2 = pd.concat(table_2_data, sort = True)
table2 = table2.rename(columns={
    'Pts.': 'Points', 'Nat.': 'Nationality','YoB': 'YearOfBirth', 'Rank' : 'Ranking',
    '1.': 'Comp_1', '2.': 'Comp_2', '3.': 'Comp_3','4.': 'Comp_4', '5.': 'Comp_5',
    '6.': 'Comp_6', '7.': 'Comp_7', '8.': 'Comp_8','9.': 'Comp_9','10.': 'Comp_10',
    '11.': 'Comp_11','12.': 'Comp_12'
})

table2.to_csv('Eurofencing_Individual_Rankings.csv', index=False)

########################################################################################################

driver.get("https://www.eurofencing.info/rankings/team-rankings")

# Select id of appropriate tag
select_gender = Select(driver.find_element(By.ID, 'gender'))
select_weapon = Select(driver.find_element(By.ID, 'weapon'))

options_gender = select_gender.options
options_weapon = select_weapon.options

# Extract text from dropdown options
options_gender_l = [i.text for i in options_gender]
options_weapon_l = [i.text for i in options_weapon]

# List to hold scraped data
table3_data = []

for gender in options_gender_l:
    for weapon in options_weapon_l:
        # Selecting id of appropriate tag
        select_gender = Select(driver.find_element(By.ID, 'gender'))
        select_weapon = Select(driver.find_element(By.ID, 'weapon'))
        
        # Select values from dropdowns
        select_gender.select_by_visible_text(gender)  # select gender
        select_weapon.select_by_visible_text(weapon)  # select weapon
        driver.find_element(By.XPATH, '//*[@id="print-rankings"]/div/form/div/div[5]/div/input').click()

        # Wait for the table to be present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        
        # Get HTML content of the page
        table_html = driver.find_element(By.TAG_NAME, 'html').get_attribute('innerHTML')
        
        # Parse the second table
        tables = pd.read_html(StringIO(table_html))
        if len(tables) > 1:
            table = tables[1]
            table['Gender'] = gender
            table['Weapon'] = weapon
            print(f"Scraping table for {gender}, {weapon}")
            table3_data.append(table)
        
        # Wait before the next iteration
        time.sleep(5)  # You can adjust the sleep time as needed

driver.quit()

# Concatenate all dataframes
final_table = pd.concat(table3_data, sort=True)
final_table = final_table.rename(columns={
    'Pts.': 'Points', 'Nat.': 'Nationality', 'Rank': 'Ranking',
    '1.': 'Comp_1', '2.': 'Comp_2', '3.': 'Comp_3', '4.': 'Comp_4', '5.': 'Comp_5',
    '6.': 'Comp_6', '7.': 'Comp_7', '8.': 'Comp_8', '9.': 'Comp_9', '10.': 'Comp_10',
    '11.': 'Comp_11', '12.': 'Comp_12'
})

# Save the final table to a CSV file
final_table.to_csv('Eurofencing_Team_Rankings.csv', index=False)

