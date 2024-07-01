from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import pandas as pd
import os

# Set up headless option
options = Options()
options.headless = True

driver = webdriver.Chrome(options=options)

# go to website
driver.get("https://www.eurofencing.info/rankings/individual-rankings")


# Select id of appropriate tag
select_gender = Select(driver.find_element(By.ID,'gender'))  # using Select from Selenium
select_weapon = Select(driver.find_element(By.ID,'weapon'))
select_age = Select(driver.find_element(By.ID,'age'))
select_year = Select(driver.find_element(By.ID,'year'))

options_gender = select_gender.options
options_weapon = select_weapon.options
options_age = select_age.options
options_year = select_year.options

options_gender_l=[i.text for i in options_gender]
options_weapon_l=[i.text for i in options_weapon]
options_age_l=[i.text for i in options_age[0:2]]
options_year_l=[i.text for i in options_year[0:5]]

# Create open lists
c=[]
table_1_data=[]
table_2_data=[]

for gender in options_gender_l:
    for weapon in options_weapon_l:
        for age in options_age_l:
            for year in options_year_l:
                # Selecting id of appropriate tag
                select_gender = Select(driver.find_element(By.ID,'gender'))
                select_weapon = Select(driver.find_element(By.ID,'weapon'))
                select_age = Select(driver.find_element(By.ID,'age'))
                select_year = Select(driver.find_element(By.ID,'year'))
                
                #select_by_visible_text() is a method of the Select class in Selenium that allows you to select an option from a drop-down list by its visible text.
                
                select_gender.select_by_visible_text(gender) # select women
                select_weapon.select_by_visible_text(weapon) # select weapon
                select_age.select_by_visible_text(age) # select age
                select_year.select_by_visible_text(year) # select year
                driver.find_element(By.XPATH, '//*[@id="print-rankings"]/div/form/div/div[6]/div/input').click() # clicking to see data

                table_html = driver.find_element(By.TAG_NAME,'html').get_attribute('innerHTML')
                    
                #table_1 = pd.read_html(table_html)[0] # get first table
                #table_1['Gender']=gender
                #table_1['Weapon']=weapon
                #table_1['Age']=age
                #table_1['Year']=year
                #print(f"Scraping table_1 for {gender}, {weapon}, {age}, {year}")
                #table_1_data.append(table_1)  # append table1 to list
                
                
                table_2 = pd.read_html(table_html)[1] # get second table
                table_2['Gender']=gender
                table_2['Weapon']=weapon
                table_2['Age']=age
                table_2['Year']=year
                print(f" Scraping table_2 for {gender}, {weapon}, {age}, {year}")
                table_2_data.append(table_2) # append table1 to list
                
                driver.implicitly_wait(10) # implicit wait not to break website with many requests.. and being blocked
                
driver.quit()

#table1 = pd.concat(table_1_data)  #concatenate all the lists together
#len(table1)

table2 = pd.concat(table_2_data, sort = True)
len(table2)

columns_t2=[ 'Rank','Pts.','Name','Nat.', 'YoB',  '1.',  '2.', '3.', '4.', '5.', '6.', '7.', '8.',
       '9.','10.', '11.', '12.', 'Age', 'Gender',   'Weapon',
       'Year']

table2=table2[columns_t2]

path=os.getcwd() #default path

#table1.to_csv(path +'\\table1new12apr2023-2.csv') 
table2.to_csv('Eurofencing_Rankings.csv')