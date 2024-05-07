import fitz
import sqlite3
import csv

def find_page_number(text1, text2):
    # Open the PDF file
    pdf_document = fitz.open('2022SeatMatrix.pdf')
    
    # Iterate through each page in the PDF
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        
        # Check if both texts are present on the same page
        if text1 in text and text2 in text:
            return True, page_num + 1  # Page numbers are 1-indexed
    return False, None

#Taking all the colleges and branchs
conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT college_name, branch FROM colleges;")
colleges = cursor.fetchall()

# Open CSV files for writing
with open('found.csv', 'w', newline='') as found_file, open('not_found.csv', 'w', newline='') as not_found_file:
    found_writer = csv.writer(found_file)
    found_writer.writerow(['College Name', 'Branch', 'Page Number'])

    not_found_writer = csv.writer(not_found_file)
    not_found_writer.writerow(['College Name', 'Branch'])

    # Iterate over colleges and branches
    for college in colleges:
        college_name, branch = college
        found, page_number = find_page_number(college_name, branch)
        if found:
            print(f"The texts '{college_name}' and '{branch}' are present on page {page_number}.")
            found_writer.writerow([college_name, branch, page_number])
        else:
            print(f"The texts '{college_name}' and '{branch}' are not present on the same page.")
            not_found_writer.writerow([college_name, branch])

# Close database connection
conn.close()
