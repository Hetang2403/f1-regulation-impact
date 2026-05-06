import snowflake.connector 
import os
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas
import pandas as pd

load_dotenv()
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA
)
df = pd.read_parquet('data/processed/team_race_panel.parquet')
df.columns = df.columns.str.upper()
write_pandas(conn, df, table_name='TEAM_RACE_PANEL',database='F1_DB', schema='RAW', overwrite=True)

df1 = pd.read_parquet('data/processed/team_race_panel_forecast.parquet')
df1.columns = df1.columns.str.upper()
write_pandas(conn, df1, table_name='TEAM_RACE_PANEL_FORECAST',database='F1_DB', schema='RAW', overwrite=True)  