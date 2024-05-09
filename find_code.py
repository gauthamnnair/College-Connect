import fitz
import sqlite3
import csv

# Connect to SQLite database
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# Retrieve distinct colleges and their corresponding minimum page numbers
cursor.execute("SELECT college_name, MIN(page_num) AS page_number FROM colleges GROUP BY college_name;")
colleges = cursor.fetchall()

# Open CSV file for writing
with open('code.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['College Name', 'Code'])

    # Open the PDF document
    pdf_document = fitz.open('2022SeatMatrix.pdf')

    # Iterate over each college
    for college, page_num in colleges:
        # Load the page
        page = pdf_document.load_page(page_num)
        # Get the text from the page and extract the first four letters
        text = page.get_text()
        code = text[:4]
        # Write the college name and its corresponding code to the CSV file
        writer.writerow([college, code])

# Close connections and files
conn.close()
pdf_document.close()

