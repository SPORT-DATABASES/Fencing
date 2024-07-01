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
        `Rank` INTEGER,
        `Name` VARCHAR(255),
        `YearOfBirth` VARCHAR(255),
        `Country` VARCHAR(255),
        `Points` FLOAT,
        `Season` VARCHAR(255),
        `Gender` VARCHAR(255),
        `Level` VARCHAR(255),
        `Weapon` VARCHAR(255),
        `Type` VARCHAR(255),
        `last_updated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    '''))

    # Truncate the table to remove all existing data
    connection.execute(text('TRUNCATE TABLE EuroF_Individ_Ranks'))

# Use df.to_sql to insert data
df.to_sql('EuroF_Individ_Ranks', con=engine, if_exists='append', index=False)
print('Data inserted successfully.')
