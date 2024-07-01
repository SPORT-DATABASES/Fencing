import pandas as pd
from sqlalchemy import create_engine, text

# Load the Eurofencing Individual Rankings CSV data
file_path = 'Eurofencing_Individual_Rankings.csv'
df = pd.read_csv(file_path)

# Database connection details
host = 'sportsdb-sports-database-for-web-scrapes.g.aivencloud.com'
port = 16439
user = 'avnadmin'
password = "AVNS_ePcujvfcmrV-r0M5UtE"
database = 'defaultdb'
ca_cert_path = 'ca.pem'

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
print('Data inserted successfully.')
