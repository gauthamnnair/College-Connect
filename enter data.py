import sqlite3
import csv
import pandas as pd


try:
    # Fetch all records from the colleges table
    c.execute("SELECT * FROM colleges")
    rows = c.fetchall()

    # Update each record, converting the percentile column to numerical type
    for row in rows:
        college_id = row[0]
        college_name = row[1]
        branch = row[2]
        percentile_str = row[5]  # Get the percentile value as a string
        try:
            # Convert the percentile string to float
            percentile = float(percentile_str)
        except ValueError:
            # Handle cases where conversion to float fails
            percentile = None

        # Update the record with the new percentile value
        c.execute("UPDATE colleges SET percentile = ? WHERE id = ?", (percentile, college_id))

    # Commit the changes to the database
    conn.commit()
    print("Percentile column updated successfully.")

except sqlite3.Error as e:
    print("Error updating percentile column:", e)

finally:
    # Close the database connection
    conn.close()

#Enter the Page Numbers of Seats Structure
def update_page_number(college_name, branch, page_number):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("UPDATE colleges SET page_num=? WHERE College_Name=? AND Branch=?", (page_number, college_name, branch))
    conn.commit()
    conn.close()

def main():
    with open('not_found.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            college_name = row['College Name']
            branch = row['Branch']
            page_number = row['Page Number']
            update_page_number(college_name, branch, page_number)
            print(f"Page number updated successfully for {college_name} - {branch} with Number {page_number}.")

# Read the CSV file
df = pd.read_csv('not_found.csv')

# Remove duplicates
df.drop_duplicates(inplace=True)

# Write back to CSV
df.to_csv('not_found.csv', index=False)


#Enter the College Code
with open('code.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        college_name = row['College Name']
        code = row['Code']
        # Connect to the database
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("UPDATE details SET code=? WHERE College_Name=?", (code,college_name))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    main()
