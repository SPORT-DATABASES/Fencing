import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details
host = 'sportsdb-sports-database-for-web-scrapes.g.aivencloud.com'
port = 16439
user = 'avnadmin'
password = os.getenv('DB_PASSWORD')
database = 'defaultdb'
ca_cert_path = 'ca.pem'

# Create SQLAlchemy engine
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}', 
                       connect_args={'ssl': {'ca': ca_cert_path}})

########## Insert Eurofencing Team Rankings into the database ##########

# Load the Eurofencing Team Rankings CSV data
file_path = 'Eurofencing_Team_Rankings.csv'
df = pd.read_csv(file_path)

# Get the column names from the SQL table
with engine.connect() as connection:
    # Truncate the table to remove old data
    connection.execute(text('TRUNCATE TABLE EuroF_Team_Ranks'))
    
    # Get the columns from the table
    result = connection.execute(text("SHOW COLUMNS FROM EuroF_Team_Ranks"))
    # Access column names using tuple indexing
    sql_columns = [row[0] for row in result]

# Filter the DataFrame to include only the columns present in the SQL table
df_filtered = df[[col for col in df.columns if col in sql_columns]]

# Insert the filtered DataFrame into the database
df_filtered.to_sql('EuroF_Team_Ranks', con=engine, if_exists='append', index=False)
print('Data inserted successfully for EuroF_Team_Ranks.')

########## Insert Eurofencing Individual Rankings into the database ##########

# Load the Eurofencing Individual Rankings CSV data
file_path = 'Eurofencing_Individual_Rankings.csv'
df = pd.read_csv(file_path)

# Get the column names from the SQL table
with engine.connect() as connection:
    # Truncate the table to remove old data
    connection.execute(text('TRUNCATE TABLE EuroF_Individ_Ranks'))
    
    # Get the columns from the table
    result = connection.execute(text("SHOW COLUMNS FROM EuroF_Individ_Ranks"))
    # Access column names using tuple indexing
    sql_columns = [row[0] for row in result]

# Filter the DataFrame to include only the columns present in the SQL table
df_filtered = df[[col for col in df.columns if col in sql_columns]]

# Insert the filtered DataFrame into the database
df_filtered.to_sql('EuroF_Individ_Ranks', con=engine, if_exists='append', index=False)
print('Data inserted successfully for Eurofencing Individual Rankings.')

########## Insert FIE Rankings into the database ##########

# Load the FIE Rankings CSV data
file_path = 'FIE_Ranking_data.csv'
df = pd.read_csv(file_path)

# Get the column names from the SQL table
with engine.connect() as connection:
    # Truncate the table to remove old data
    connection.execute(text('TRUNCATE TABLE fie_rankings'))
    
    # Get the columns from the table
    result = connection.execute(text("SHOW COLUMNS FROM fie_rankings"))
    # Access column names using tuple indexing
    sql_columns = [row[0] for row in result]

# Filter the DataFrame to include only the columns present in the SQL table
df_filtered = df[[col for col in df.columns if col in sql_columns]]

# Insert the filtered DataFrame into the database
df_filtered.to_sql('fie_rankings', con=engine, if_exists='append', index=False)
print('Data inserted successfully for FIE rankings.')
