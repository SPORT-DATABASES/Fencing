import requests
import pandas as pd
import urllib3
import os

from fpdf import FPDF
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

######## 1. Scrape Rankings data from FIE website

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://fie.org/athletes'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

weapons = ['e', 'f', 's']
levels = ['s', 'j']
genders = ['m', 'f']
types = ['i', 'e']

all_athletes_data = []

for weapon in weapons:
    for level in levels:
        for gender in genders:
            for type in types:
                # Define the payload for the current combination
                payload = {
                    "weapon": weapon,
                    "level": level,
                    "type": type,
                    "gender": gender,
                    "isTeam": False,
                    "isSearch": False,
                    "country": "",
                    "fetchPage": 1,
                    "name": ""
                }

                response = requests.post(url, headers=headers, json=payload, verify=False)
                if response.status_code == 200:
                    data = response.json()
                    all_athletes = data.get('allAthletes', [])
                    
                    for athlete in all_athletes:
                        athlete['type'] = type
                    all_athletes_data.extend(all_athletes)
                else:
                    print(f"Failed to fetch data for weapon: {weapon}, level: {level}, gender: {gender}, type: {type}. Status code: {response.status_code}")

df = pd.DataFrame(all_athletes_data)

df['type'] = df['type'].replace({'i': 'Individual', 'e': 'Team'})
df['weapon'] = df['weapon'].replace({'E': 'Epee', 'F': 'Foil', 'S': 'Sabre'})
df['hand'] = df['hand'].replace({'L': 'Left', 'R': 'Right'})
df['level'] = df['level'].replace({'S': 'Senior', 'J': 'Junior'})
df['gender'] = df['gender'].replace({'M': 'Men', 'F': 'Women'})

######## 2. Get ISO codes from wikipedia to make country column

url = 'https://en.wikipedia.org/wiki/Comparison_of_alphabetic_country_codes'
tables = pd.read_html(url)
country_codes_table = tables[0].drop(columns=['Flag', 'FIFA', tables[0].columns[-1]])

rankings_df = df.merge(country_codes_table, left_on='flag', right_on='IOC', how='left')

rankings_df.rename(columns={'Country': 'country_2', 'id': 'Fencerid'}, inplace=True)
rankings_df.rename(columns=lambda x: x.capitalize() if x not in ['IOC', 'ISO'] else x, inplace=True)

print(rankings_df.head())
print(rankings_df.tail())
print(f"Total number of athletes collected: {len(all_athletes_data)}")

rankings_df.to_csv('FIE_Ranking_data.csv', index=False)
