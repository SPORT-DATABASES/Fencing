
######## PDF and emails

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

###### Set Nationality to filter on     

FIE_team = "QATAR"
EuroF_Nationality = "QAT"

#######################

FIE_rankings_df = pd.read_csv('FIE_Ranking_data.csv')
FIE_rankings_df = FIE_rankings_df[FIE_rankings_df['Country'] == FIE_team]
FIE_rankings_df = FIE_rankings_df[['Name', 'Rank', 'Points', 'Gender', 'Level', 'Weapon', 'Type']].drop_duplicates()

EuroF_rankings_df = pd.read_csv('Eurofencing_Individual_Rankings.csv')
EuroF_rankings_df = EuroF_rankings_df[EuroF_rankings_df['Nationality'] == 'QAT']

EuroF_rankings_df = EuroF_rankings_df[['Name', 'Ranking', 'Points', 'Gender', 'Age', 'Weapon']].drop_duplicates()

EuroF_rankings_df.rename(columns={'Ranking': 'Rank', 'Age': 'Level'}, inplace=True)
EuroF_rankings_df['Type'] = 'Individual'

### Need to scrape for Teams in EuroF and add to code 

EuroF_team_rankings_df = pd.read_csv('Eurofencing_Team_Rankings.csv')
EuroF_team_rankings_df = EuroF_team_rankings_df[EuroF_team_rankings_df['Nationality'] == 'QAT']
EuroF_team_rankings_df['Type'] ='Team'
EuroF_team_rankings_df['Level'] ='Cadets'
EuroF_team_rankings_df = EuroF_team_rankings_df[['Name', 'Ranking', 'Points', 'Gender', 'Level', 'Weapon', 'Type']].drop_duplicates()
EuroF_team_rankings_df.rename(columns={'Ranking': 'Rank'}, inplace=True)

# Split into individuals and teams
FIE_individuals_df = FIE_rankings_df[FIE_rankings_df['Type'] == 'Individual']   # change the FIE when adding Eurofencing
FIE_teams_df = FIE_rankings_df[FIE_rankings_df['Type'] == 'Team']

EuroF_individuals_df = EuroF_rankings_df[EuroF_rankings_df['Type'] == 'Individual']   # change the FIE when adding Eurofencing
EuroF_teams_df = EuroF_team_rankings_df[EuroF_team_rankings_df['Type'] == 'Team']

individuals_df = pd.concat([EuroF_individuals_df, FIE_individuals_df], ignore_index=True)
teams_df = pd.concat([EuroF_teams_df, FIE_teams_df], ignore_index=True)

# Sort the DataFrames: Men first, then Women; Seniors first, then Juniors
for df in [individuals_df, teams_df]:
    df['Gender'] = pd.Categorical(df['Gender'], categories=['Men', 'Women'], ordered=True)
    df['Level'] = pd.Categorical(df['Level'], categories=['Senior', 'Junior', 'Cadets'], ordered=True)
    df.sort_values(by=['Gender', 'Level', 'Weapon', 'Rank'], inplace=True)


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
        self.set_font('Arial', 'B', 16)  # Set font size to 16 for headers
        self.cell(0, 10, title, 0, 1, 'C')
        self.ln(2)
        self.dashed_line(10, self.get_y(), 200, self.get_y())  # Add dashed line
        self.ln(5)  # Add a small space after the title

    def chapter_body(self, title, data):
        self.set_font('Arial', '', 12)
        col_widths = [105, 18, 20, 23, 25]  # Define column widths: Name, Rank, Points, AgeGroup, Weapon
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

################Create the email

sender_email = "kennymcmillan29@gmail.com"
receiver_emails = ["kennymcmillan29@gmail.com" ,"massimo.omeri@aspire.qa"]
password = "lcsc pcuy pgxb zcri"

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