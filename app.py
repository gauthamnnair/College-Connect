from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to create the database table if it doesn't exist
def create_table():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT NOT NULL UNIQUE,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def index():
    return render_template('index.html')

# Render the signup.html template for the sign-up page
@app.route('/signup/', methods=['GET'])
def signup_form():
    return render_template('signup.html')

# Function to handle signup form submission
@app.route('/signup/', methods=['POST'])
def signup():
    email = request.form['signupEmail']
    username = request.form['signupUsername']
    password = request.form['signupPassword']
    repeat_password = request.form['signupRepeatPassword']

    # Here you would typically validate the form data
    # and perform the signup logic, such as checking if the email already exists,
    # hashing the password, and saving the user to the database.

    # For simplicity, let's just print the form data
    print("Email:", email)
    print("Username:", username)
    print("Password:", password)
    print("Repeat Password:", repeat_password)

    # Redirect the user to a success page or a login page
    return redirect(url_for('signup_success'))

# Route for showing a success message after signup
@app.route('/signup_success')
def signup_success():
    return "Signup successful! You can now login."

if __name__ == '__main__':
    app.run(port=8000, debug=True)

