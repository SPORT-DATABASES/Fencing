
import os
import pandas as pd 
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


load_dotenv()

# Database connection details
host = 'sportsdb-sports-database-for-web-scrapes.g.aivencloud.com'
port = 16439
user = 'avnadmin'
password = os.getenv('DB_PASSWORD')
database = 'defaultdb'
ca_cert_path = 'ca.pem'

############ Firstly, inserting Eurofencing Individual Rankings into the database

# Load the Eurofencing Individual Rankings CSV data
file_path = 'Eurofencing_Individual_Rankings.csv'
df = pd.read_csv(file_path)

# Create SQLAlchemy engine
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}', connect_args={'ssl': {'ca': ca_cert_path}})

with engine.connect() as connection:
    connection.execute(text('''
    CREATE TABLE IF NOT EXISTS EuroF_Individ_Ranks (
        	`id` INT AUTO_INCREMENT PRIMARY KEY,
    Comp_1 VARCHAR(255),
    Comp_2 VARCHAR(255),
    Comp_3 VARCHAR(255),
    Comp_4 VARCHAR(255),
    Comp_5 VARCHAR(255),
    Comp_6 VARCHAR(255),
    Comp_7 VARCHAR(255),
    Comp_8 VARCHAR(255),
    Comp_9 VARCHAR(255),
    Comp_10 VARCHAR(255),
    Comp_11 VARCHAR(255),
    Comp_12 VARCHAR(255),
    Age VARCHAR(255),
    Gender VARCHAR(255),
    Name VARCHAR(255),
    Nationality VARCHAR(255),
    Points FLOAT,
    Ranking INT,
    Weapon VARCHAR(255),
    Year VARCHAR(255),
    YearOfBirth INT,
        `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    '''))

    # Truncate the table to remove all existing data
    connection.execute(text('TRUNCATE TABLE EuroF_Individ_Ranks'))

# Use df.to_sql to insert data
df.to_sql('EuroF_Individ_Ranks', con=engine, if_exists='append', index=False)
print('Data inserted successfully for Eurofencing.')

################ Now inserting FIE Rankings into Database

# Load CSV data
df = pd.read_csv('FIE_Rankings.csv')

with engine.connect() as connection:
    connection.execute(text('''
    CREATE TABLE IF NOT EXISTS fie_rankings (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `Rank` INTEGER,
        `Points` FLOAT,
        `Name` VARCHAR(255),
        `Country` VARCHAR(255),
        `Hand` VARCHAR(255),
        `Age` INTEGER,
        `Category` VARCHAR(255),
        `Scrape_Date` VARCHAR(255),
        `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    '''))

    # Truncate the table to remove all existing data
    connection.execute(text('TRUNCATE TABLE fie_rankings'))

# Use df.to_sql to insert data
df.to_sql('fie_rankings', con=engine, if_exists='append', index=False)
print('Data inserted successfully for FIE rankings.')
