import pymysql
import pandas as pd

# MySQL connection settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'lead_scoring_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Create MySQL connection
def get_connection():
    return pymysql.connect(**DB_CONFIG)

# Create leads table if not exists
def create_table():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    Company VARCHAR(255),
                    Website TEXT,
                    Industry VARCHAR(100),
                    ProductCategory VARCHAR(100),
                    BusinessType VARCHAR(50),
                    EmployeesCount INT,
                    Revenue VARCHAR(50),
                    Revenue_num FLOAT,
                    YearFounded INT,
                    BBBRating VARCHAR(10),
                    City VARCHAR(100),
                    State VARCHAR(50),
                    LeadScore FLOAT
                )
            """)
        conn.commit()

# Insert scored leads into the database
def insert_leads(df):
    df = df.copy()
    df.rename(columns={
        'Product/Service Category': 'ProductCategory',
        'Business Type': 'BusinessType',
        'Employees Count': 'EmployeesCount',
        'Year Founded': 'YearFounded',
        'BBB Rating': 'BBBRating',
        'Lead Score': 'LeadScore'
    }, inplace=True)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO leads (
                        Company, Website, Industry, ProductCategory,
                        BusinessType, EmployeesCount, Revenue, Revenue_num,
                        YearFounded, BBBRating, City, State, LeadScore
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    row.get('Company'),
                    row.get('Website'),
                    row.get('Industry'),
                    row.get('ProductCategory'),
                    row.get('BusinessType'),
                    row.get('EmployeesCount'),
                    row.get('Revenue'),
                    row.get('Revenue_num'),
                    row.get('YearFounded'),
                    row.get('BBBRating'),
                    row.get('City'),
                    row.get('State'),
                    row.get('LeadScore')
                ))
        conn.commit()

# Fetch raw leads (no LeadScore)
def fetch_leads(raw_only=False):
    query = "SELECT * FROM leads WHERE LeadScore IS NULL" if raw_only else "SELECT * FROM leads"
    with get_connection() as conn:
        return pd.read_sql(query, conn)

# Fetch scored leads (sorted by score)
def fetch_leads_with_scores():
    query = "SELECT * FROM leads WHERE LeadScore IS NOT NULL ORDER BY LeadScore DESC"
    with get_connection() as conn:
        return pd.read_sql(query, conn)
