import sqlite3
import csv

# Function to create the database table if it doesn't exist
def create_table():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS colleges
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 college_name TEXT NOT NULL,
                 score_type TEXT NOT NULL,
                 seat_type TEXT NOT NULL,
                 branch TEXT NOT NULL,
                 percentile FLOAT NOT NULL)''')
    conn.commit()
    conn.close()

create_table()

# Function to insert data from CSV into the database
def insert_data_from_csv(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            college_name = row['college_name']
            score_type = row['score_type']
            seat_type = row['seat_type']
            branch = row['branch']
            percentile = float(row['min'])
            conn = sqlite3.connect('data.db')
            c = conn.cursor()
            c.execute("INSERT INTO colleges (college_name, score_type, seat_type, branch, percentile) VALUES (?, ?, ?, ?, ? )",
                      (college_name, score_type, seat_type, branch, percentile))
            conn.commit()
            conn.close()

# Call the function to insert data from CSV into the database
insert_data_from_csv('data.csv')

