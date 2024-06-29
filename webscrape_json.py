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

rankings_df.rename(columns={'Country': 'country_2'}, inplace=True)
rankings_df.rename(columns=lambda x: x.capitalize() if x not in ['IOC', 'ISO'] else x, inplace=True)

print(rankings_df.head())
print(rankings_df.tail())
print(f"Total number of athletes collected: {len(all_athletes_data)}")

rankings_df.to_csv('Ranking_data.csv', index=False)


######## 3. PDF and email

team = "QATAR"

sender_email = "kennymcmillan29@gmail.com"
receiver_emails = ["kennymcmillan29@gmail.com"]
password = "sqzi vduz elbn jyna"

rankings_df = rankings_df[rankings_df['Country'] == team]
#rankings_df = rankings_df.drop(columns=['Id', 'Country_2'])

rankings_df = rankings_df[['Name', 'Rank', 'Points', 'Gender', 'Level', 'Weapon', 'Type']].drop_duplicates()

# Split into individuals and teams
individuals_df = rankings_df[rankings_df['Type'] == 'Individual']
teams_df = rankings_df[rankings_df['Type'] == 'Team']


# Sort the DataFrames: Men first, then Women; Seniors first, then Juniors
for df in [individuals_df, teams_df]:
    df['Gender'] = pd.Categorical(df['Gender'], categories=['Men', 'Women'], ordered=True)
    df['Level'] = pd.Categorical(df['Level'], categories=['Senior', 'Junior'], ordered=True)
    df.sort_values(by=['Gender', 'Level', 'Weapon'], inplace=True)

# Print DataFrame for debugging
print(individuals_df.head())
print(teams_df.head())

# Get the current date
update_date = datetime.now().strftime('%Y-%m-%d')

print("Generating PDF report...")
class PDF(FPDF):
    def header(self):
        if self.page == 1:  # Only add header on the first page
            self.image('qatar_flag.png', 10, 8, 33)  # Add the qatar flag image
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Weekly Ranking Report', 0, 1, 'C')
            self.cell(0, 10, f'Update Date: {update_date}', 0, 1, 'C')
            self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)  # Add a small space after the title

    def chapter_body(self, title, data):
        self.set_font('Arial', '', 12)
        col_widths = [70, 30, 30, 30, 30]  # Define column widths: Name, Rank, Points, AgeGroup, Weapon
        self.set_fill_color(200, 220, 255)

        # Calculate the height of the table
        table_height = (len(data) + 1) * 10  # Each row is 10 units high, +1 for the header

        # Check if the table fits on the current page, else add a new page
        if self.get_y() + table_height > self.h - self.b_margin:
            self.add_page()
        
        # Add the title
        self.chapter_title(title)

        # Add table header
        for col, width in zip(data.columns, col_widths):
            self.cell(width, 10, col, 1, 0, 'C', 1)
        self.ln()

        # Add table rows with alternating row colors
        fill = False
        for row in data.itertuples(index=False):
            if self.get_y() + 10 > self.h - self.b_margin:
                self.add_page()
                self.chapter_title(title)  # Re-add the title on the new page
                for col, width in zip(data.columns, col_widths):
                    self.cell(width, 10, col, 1, 0, 'C', 1)
                self.ln()
            self.set_fill_color(240, 240, 240) if fill else self.set_fill_color(255, 255, 255)
            for item, width in zip(row, col_widths):
                self.cell(width, 10, str(item), 1, 0, 'C', fill)
            self.ln()
            fill = not fill
        self.ln()  # Add a space after each table

# Create PDF
pdf = PDF()
pdf.add_page()

# Generate the report for individual athletes
pdf.chapter_title('Individual Rankings')
for (gender, level, weapon), group in individuals_df.groupby(['Gender', 'Level', 'Weapon'], observed=True):
    title = f'{weapon} - {gender} - {level}'
    print(f"Adding table for {title}")
    pdf.chapter_body(title, group[['Name', 'Rank', 'Points', 'Level', 'Weapon']])

# Start a new page for the team rankings
pdf.add_page()

# Generate the report for team athletes
pdf.chapter_title('Team Rankings')
for (gender, level, weapon), group in teams_df.groupby(['Gender', 'Level', 'Weapon'], observed=True):
    title = f'{weapon} - {gender} - {level}'
    print(f"Adding table for {title}")
    pdf.chapter_body(title, group[['Name', 'Rank', 'Points', 'Level', 'Weapon']])

output_dir = 'Ranking_PDF_reports'
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

# Create the filename with the current date
filename = os.path.join(output_dir, f'Fencing_Ranking_Report_{update_date}.pdf')
pdf.output(filename)
print(f"PDF report saved as {filename}")


print("Sending email with PDF report...")
# Send email with the PDF report
subject = "Weekly Ranking Report"
body = "Please find attached the latest Fencing Athlete Rankings report."

# Create the email
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = ", ".join(receiver_emails)
msg['Subject'] = subject

msg.attach(MIMEText(body, 'plain'))

# Attach the PDF
with open(filename, "rb") as attachment:
    part = MIMEApplication(attachment.read(), _subtype="pdf")
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(part)

# Send the email
with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Using Gmail's SMTP server
    server.starttls()
    server.login(sender_email, password)
    server.send_message(msg)

print('PDF report generated and emailed successfully.')
