
######## PDF and email

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

team = "QATAR"

FIE_rankings_df = pd.read_csv('FIE_ranking_data.csv')

FIE_rankings_df = FIE_rankings_df[FIE_rankings_df['Country'] == team]
#rankings_df = rankings_df.drop(columns=['Id', 'Country_2'])

FIE_rankings_df = FIE_rankings_df[['Name', 'Rank', 'Points', 'Gender', 'Level', 'Weapon', 'Type']].drop_duplicates()

########## add in Eurofencing scrape, make datatable and append to FIE_rankings_df
#### then make rankings_df table and run next code.
#### Need to amend the age group and type (team and individual for the append)


# Split into individuals and teams
individuals_df = FIE_rankings_df[FIE_rankings_df['Type'] == 'Individual']   # change the FIE when adding Eurofencing
teams_df = FIE_rankings_df[FIE_rankings_df['Type'] == 'Team']

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

################Create the email

sender_email = "kennymcmillan29@gmail.com"
receiver_emails = ["kennymcmillan29@gmail.com", "massimo.omeri@aspire.qa"]
password = "sqzi vduz elbn jyna"

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