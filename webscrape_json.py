import requests
import pandas as pd

# Define the URL
url = 'https://fie.org/athletes'

# Define the essential headers
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Define the possible values for weapon, level, and gender
weapons = ['e', 'f', 's']
levels = ['s', 'j']
genders = ['m', 'f']

# Initialize an empty list to store all athletes data
all_athletes_data = []

# Iterate through all combinations of weapon, level, and gender
for weapon in weapons:
    for level in levels:
        for gender in genders:
            # Define the payload for the current combination
            payload = {
                "weapon": weapon,
                "level": level,
                "type": "i",
                "gender": gender,
                "isTeam": False,
                "isSearch": False,
                "country": "",
                "fetchPage": 1,
                "name": ""
            }

            # Send the POST request
            response = requests.post(url, headers=headers, json=payload)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                
                # Extract the allAthletes data
                all_athletes = data.get('allAthletes', [])
                
                # Append the athletes data to the list
                all_athletes_data.extend(all_athletes)
            else:
                print(f"Failed to fetch data for weapon: {weapon}, level: {level}, gender: {gender}. Status code: {response.status_code}")

# Convert the list of athletes data to a DataFrame
df = pd.DataFrame(all_athletes_data)

# Display the DataFrame (optional)
print(df)

# Optionally, save the DataFrame to a CSV file
df.to_csv('Ranking_data.csv', index=False)

# Optionally, print the total number of athletes collected
print(f"Total number of athletes collected: {len(all_athletes_data)}")
