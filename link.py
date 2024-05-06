import sqlite3
import pyautogui
import time
import pyperclip

# Function to retrieve distinct college names from the database
def retrieve_distinct_college_names():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT college_name FROM colleges WHERE college_name NOT IN (SELECT college_name FROM details)")
    college_names = cursor.fetchall()
    return college_names

# Function to find the website link for a given college name using PyAutoGUI
def find_website_link_with_pyautogui(college_name):
    print(f"Searching for '{college_name}'...")

    # Open a new tab in the browser
    pyautogui.hotkey('ctrl', 't')
    time.sleep(1)  # Wait for the new tab to open

    # Type the search query
    pyautogui.write(f"{college_name} website")
    pyautogui.press('enter')
    time.sleep(3)  # Wait for the search results to load

    # Navigate to the first link using arrow keys
    pyautogui.press('down')  # Move to the first search result
    pyautogui.press('enter')  # Open the link 
    time.sleep(4)  # Wait for the page to load

    # Select and copy the URL (Ctrl + L to select the address bar, Ctrl + C to copy)
    pyautogui.hotkey('ctrl', 'l')
    pyautogui.hotkey('ctrl', 'a')  # Select all text
    pyautogui.hotkey('ctrl', 'c')  # Copy
    time.sleep(1)  # Wait for copying to complete
    pyautogui.hotkey('ctrl', 'w')

    # Get the copied URL from the clipboard
    website_link = pyperclip.paste()

    return website_link

def insert_details_into_table(college_name, website_link):
    # Connect to the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Insert college name and website link into the details table
    cursor.execute("INSERT INTO details (college_name, website_link) VALUES (?, ?)", (college_name, website_link))
    
    # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()

# Main function
def main():
    c = 0
    pyautogui.press('win')  # Press Windows key to open Start menu
    time.sleep(0.5)  # Wait for Start menu to appear
    pyautogui.write('librewolf')  # Type the name of the browser
    time.sleep(1)  # Wait for search results to appear
    pyautogui.press('enter')  # Open Firefox
    time.sleep(2) 
    # Retrieve distinct college names
    college_names = retrieve_distinct_college_names()

    # Process each college name
    for college in college_names:
        college_name = college[0]
        
        # Find the website link for the college using PyAutoGUI
        website_link = find_website_link_with_pyautogui(college_name)
        
        # Insert college name and website link into the details table
        if website_link:
            insert_details_into_table(college_name, website_link)
            print(f"Website link for {college_name}: {website_link}")
        else:
            print(f"No website link found for {college_name}")
            c += 1
    print(c)
# Entry point
if __name__ == "__main__":
    main()

