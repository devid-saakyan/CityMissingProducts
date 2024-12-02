import sqlite3
from datetime import datetime

db_path = "db.sqlite3"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cutoff_date = datetime(2024, 12, 1, 0, 0, 0)


def convert_to_iso(date_string):
    if not date_string:
        return None
    try:
        parsed_date = datetime.strptime(date_string, "%m/%d/%Y %I:%M:%S %p")
        return parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

table_name = "main_productsreport"
date_column_name = "date"

cursor.execute(f"PRAGMA table_info({table_name})")
columns = cursor.fetchall()
date_column_index = next((i for i, col in enumerate(columns) if col[1] == date_column_name), None)

if date_column_index is None:
    raise ValueError(f"Column '{date_column_name}' not found in table '{table_name}'.")

cursor.execute(f"SELECT * FROM {table_name}")
rows = cursor.fetchall()

filtered_rows = [
    row for row in rows
    if convert_to_iso(row[date_column_index]) and datetime.strptime(convert_to_iso(row[date_column_index]), "%Y-%m-%d %H:%M:%S") >= cutoff_date
]

cursor.execute(f"DELETE FROM {table_name}")

column_names = [col[1] for col in columns]

insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(['?' for _ in column_names])})"

for row in filtered_rows:
    cursor.execute(insert_query, row)

connection.commit()

connection.close()

print(f"Оставлено записей: {len(filtered_rows)}")
