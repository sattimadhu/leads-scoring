import pymysql
import pandas as pd
import re
from sqlalchemy import create_engine

# MySQL connection settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345678',
    'database': 'lead_scoring_db',
    'charset': 'utf8mb4',
}

def get_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )

def get_engine():
    url = (
        f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"
    )
    engine = create_engine(url)
    return engine

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    Company VARCHAR(255) UNIQUE,
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

def revenue_to_number(rev_str):
    """
    Convert revenue string like '$1M-$10M', '$500K-$1M', '$50M+' to an approximate float number.
    """
    if not isinstance(rev_str, str):
        return None
    
    rev_str = rev_str.replace("$", "").replace(",", "").strip().upper()

    # Handle ranges like '1M-10M'
    range_match = re.match(r'(\d+\.?\d*)[MK]?-(\d+\.?\d*)[MK]?', rev_str)
    if range_match:
        low, high = float(range_match.group(1)), float(range_match.group(2))
        low_mult = 1e6 if "M" in rev_str else (1e3 if "K" in rev_str else 1)
        high_mult = 1e6 if "M" in rev_str else (1e3 if "K" in rev_str else 1)
        return ((low * low_mult) + (high * high_mult)) / 2

    # Handle single values like '50M+', '500K'
    single_match = re.match(r'(\d+\.?\d*)([MK])?\+?', rev_str)
    if single_match:
        number = float(single_match.group(1))
        multiplier = 1e6 if single_match.group(2) == "M" else 1e3 if single_match.group(2) == "K" else 1
        return number * multiplier

    return None

def insert_leads(df):
    df = df.copy()

    # Rename columns to match DB schema
    df.rename(columns={
        'Product/Service Category': 'ProductCategory',
        'Business Type': 'BusinessType',
        'Employees Count': 'EmployeesCount',
        'Year Founded': 'YearFounded',
        'BBB Rating': 'BBBRating',
        'Lead Score': 'LeadScore'
    }, inplace=True)

    # Calculate Revenue_num if missing or null
    if 'Revenue_num' not in df.columns:
        df['Revenue_num'] = df['Revenue'].apply(revenue_to_number)
    else:
        df['Revenue_num'] = df.apply(
            lambda row: revenue_to_number(row['Revenue']) if pd.isnull(row['Revenue_num']) else row['Revenue_num'],
            axis=1
        )

    with get_connection() as conn:
        with conn.cursor() as cursor:
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO leads (
                        Company, Website, Industry, ProductCategory,
                        BusinessType, EmployeesCount, Revenue, Revenue_num,
                        YearFounded, BBBRating, City, State, LeadScore
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        Website=VALUES(Website),
                        Industry=VALUES(Industry),
                        ProductCategory=VALUES(ProductCategory),
                        BusinessType=VALUES(BusinessType),
                        EmployeesCount=VALUES(EmployeesCount),
                        Revenue=VALUES(Revenue),
                        Revenue_num=VALUES(Revenue_num),
                        YearFounded=VALUES(YearFounded),
                        BBBRating=VALUES(BBBRating),
                        City=VALUES(City),
                        State=VALUES(State),
                        LeadScore=VALUES(LeadScore)
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

def fetch_leads(raw_only=False):
    query = "SELECT * FROM leads WHERE LeadScore IS NULL" if raw_only else "SELECT * FROM leads"
    engine = get_engine()
    df = pd.read_sql(query, engine)
    return df

def fetch_leads_with_scores():
    query = "SELECT * FROM leads WHERE LeadScore IS NOT NULL ORDER BY LeadScore DESC"
    engine = get_engine()
    df = pd.read_sql(query, engine)
    return df 
