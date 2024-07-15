
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

########### Insert Eurofencing Team Rankings into the database

# Load the CSV data

df = pd.read_csv('Eurofencing_Team_Rankings.csv')

with engine.connect() as connection:
    connection.execute(text('''
    CREATE TABLE IF NOT EXISTS EuroF_Team_Ranks (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `Comp_1` VARCHAR(255),
        `Comp_2` VARCHAR(255),
        `Comp_3` VARCHAR(255),
        `Comp_4` VARCHAR(255),
        `Comp_5` VARCHAR(255),
        `Comp_6` VARCHAR(255),
        `Comp_7` VARCHAR(255),
        `Comp_8` VARCHAR(255),
        `Comp_9` VARCHAR(255),
        `Comp_10` VARCHAR(255),
        `Comp_11` VARCHAR(255),
        `Comp_12` VARCHAR(255),
        `Gender` VARCHAR(50),
        `Name` VARCHAR(255),
        `Nationality` VARCHAR(255),
        `Points` FLOAT,
        `Ranking` INT,
        `Weapon` VARCHAR(50),
        `Scrape_Date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    '''))

    # Truncate the table to remove all existing data
    connection.execute(text('TRUNCATE TABLE EuroF_Team_Ranks'))

# Use df.to_sql to insert data
df.to_sql('EuroF_Team_Ranks', con=engine, if_exists='append', index=False)
print('Data inserted successfully for EuroF_Team_Ranks.')

################ Now inserting FIE Rankings into Database

# Load CSV data
df = pd.read_csv('FIE_Ranking_data.csv')

with engine.connect() as connection:
    connection.execute(text('''
    CREATE TABLE IF NOT EXISTS fie_rankings (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `Fencerid` INT,
        `Name` VARCHAR(255),
        `Age` INT,
        `Country` VARCHAR(255),
        `Weapon` VARCHAR(255),
        `Gender` VARCHAR(50),
        `Points` FLOAT,
        `Date` DATE,
        `Level` VARCHAR(50),
        `Hand` VARCHAR(50),
        `Height` FLOAT,
        `Rank` INT,
        `Flag` VARCHAR(50),
        `Image` VARCHAR(255),
        `Type` VARCHAR(50),
        `Country_2` VARCHAR(255),
        `IOC` VARCHAR(50),
        `ISO` VARCHAR(50),
        `Scrape_Date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    '''))

    # Truncate the table to remove all existing data
    connection.execute(text('TRUNCATE TABLE fie_rankings'))

# Use df.to_sql to insert data
df.to_sql('fie_rankings', con=engine, if_exists='append', index=False)
print('Data inserted successfully for FIE rankings.')