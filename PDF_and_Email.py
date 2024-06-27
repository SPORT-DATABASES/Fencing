import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Email configuration
sender_email = "kennymcmillan29@gmail.com"
receiver_emails = ["kennymcmillan29@gmail.com"]
password = "sqzi vduz elbn jyna"

print("Loading rankings data...")
rankings_df = pd.read_csv('Rankings.csv')

# Filter for country 'United Arab Emirates'
qatar_rankings_df = rankings_df[rankings_df['Country'] == 'QATAR']
qatar_rankings_df = qatar_rankings_df.drop(columns=['id', 'Country'])

# Ensure necessary columns are in the DataFrame and remove duplicates
qatar_rankings_df = qatar_rankings_df[['Name', 'Rank', 'Points', 'Category']].drop_duplicates()

print("Extracting category info...")
# Extract Weapon, Gender, and AgeGroup from Category
def extract_category_info(category):
    parts = category.split('_')
    weapon = parts[0]
    gender = parts[1]
    age_group = parts[2]
    return weapon, gender, age_group

qatar_rankings_df[['Weapon', 'Gender', 'AgeGroup']] = qatar_rankings_df['Category'].apply(lambda x: pd.Series(extract_category_info(x)))

# Sort the DataFrame: Men first, then Women; Seniors first, then Juniors
qatar_rankings_df['Gender'] = pd.Categorical(qatar_rankings_df['Gender'], categories=['Men', 'Women'], ordered=True)
qatar_rankings_df['AgeGroup'] = pd.Categorical(qatar_rankings_df['AgeGroup'], categories=['Senior', 'Junior'], ordered=True)
qatar_rankings_df = qatar_rankings_df.sort_values(by=['Gender', 'AgeGroup', 'Weapon'])

# Print DataFrame for debugging
print(qatar_rankings_df.head())

# Get the current date
update_date = datetime.now().strftime('%Y-%m-%d')

print("Generating PDF report...")
# Generate PDF report
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

    def chapter_body(self, data):
        self.set_font('Arial', '', 12)
        col_widths = [70, 30, 30, 30, 30]  # Define column widths: Name, Rank, Points, AgeGroup, Weapon
        # Check if there's enough space on the page for the table and title
        if self.get_y() + len(data) * 10 + 30 > self.h - self.b_margin:
            self.add_page()
        # Add table header
        self.set_fill_color(200, 220, 255)
        for col, width in zip(data.columns, col_widths):
            self.cell(width, 10, col, 1, 0, 'C', 1)
        self.ln()
        # Add table rows with alternating row colors
        fill = False
        for row in data.itertuples(index=False):
            self.set_fill_color(240, 240, 240) if fill else self.set_fill_color(255, 255, 255)
            for item, width in zip(row, col_widths):
                self.cell(width, 10, str(item), 1, 0, 'C', fill)
            self.ln()
            fill = not fill
        self.ln()  # Add a space after each table

# Create PDF
pdf = PDF()
pdf.add_page()

# Group the DataFrame by 'Weapon', 'Gender', and 'AgeGroup' and create a table for each group
for (gender, agegroup, weapon), group in qatar_rankings_df.groupby([ 'Gender', 'AgeGroup', 'Weapon'], observed=True):
    title = f'{weapon} - {gender} - {agegroup}'
    print(f"Adding table for {title}")
    # Check if there's enough space for the title and the table
    if pdf.get_y() + len(group) * 10 + 30 > pdf.h - pdf.b_margin:
        pdf.add_page()
    pdf.chapter_title(title)
    pdf.chapter_body(group[['Name', 'Rank', 'Points', 'AgeGroup', 'Weapon']])

# Create the directory if it doesn't exist
output_dir = 'Ranking_PDF_reports'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

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
