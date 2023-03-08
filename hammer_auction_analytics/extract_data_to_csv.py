import sqlite3

import pandas as pd

DATABASE_PATH = "db/db.sqlite"
OUTPUT_PATH = 'extracted_data/buckowski_data.csv'

QUERY = """
SELECT
    *
FROM lots
LEFT JOIN auctions ON auctions.id = lots.auction_id
"""

connection = sqlite3.connect(DATABASE_PATH)

data = pd.read_sql(QUERY, connection)
data.to_csv(OUTPUT_PATH, sep=',')