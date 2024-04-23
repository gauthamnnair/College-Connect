from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to create the database table if it doesn't exist
def create_table():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     email TEXT NOT NULL UNIQUE,
                     username TEXT NOT NULL,
                     password TEXT NOT NULL)''')

# Function to create the admissions table if it doesn't exist
def create_admissions_table():
    with sqlite3.connect('admissions.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS admissions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     mhcet_percentile FLOAT NOT NULL,
                     jee_percentile FLOAT NOT NULL,
                     category TEXT NOT NULL)''')

# Create tables on startup
create_table()
create_admissions_table()

# Render the home page
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Render the sign-up page
@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('signup.html')

# Handle sign-up form submission
@app.route('/signup', methods=['POST'])
def signup():
    # Extract form data
    email = request.form['signupEmail']
    username = request.form['signupUsername']
    password = request.form['signupPassword']
    repeat_password = request.form['signupRepeatPassword']

    # Check if passwords match
    if password != repeat_password:
        return "Passwords do not match. Please try again."

    # Check if email is already registered
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            return "Email is already registered. Please use a different email."

        # Insert user data into the database
        c.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, password))

    # Redirect to login page after successful signup
    return redirect(url_for('login_form'))

# Render the login page
@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

# Handle login form submission
@app.route('/login', methods=['POST'])
def login():
    # Extract form data
    username = request.form['loginUsername']
    password = request.form['loginPassword']

    # Authenticate user
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

    if user:
        # Redirect to index page with username if login is successful
        return redirect(url_for('index', username=username))
    else:
        # Redirect back to login page with an error message
        return redirect(url_for('login_form'))

# Route for the index page with username
@app.route('/index/<username>')
def index(username):
    return f'Welcome, {username}!'

# Render the admission form
@app.route('/admission', methods=['GET'])
def admission_form():
    return render_template('form.html')

# Handle admission form submission
@app.route('/submit', methods=['POST'])
def submit_admission():
    mhcet_percentile = request.form.get('mhcet_percentile')
    jee_percentile = request.form.get('jee_percentile')
    category = request.form.get('category') + 'S'  # Assuming category is concatenated with 'S'
    colleges, distinct_branches = filter_colleges(mhcet_percentile, jee_percentile, category)

    # Pass data to the result.html template
    return render_template('result.html', colleges=colleges, distinct_branches=distinct_branches, mhcet_percentile=mhcet_percentile, jee_percentile=jee_percentile, category=category)

# Function to fetch colleges from the database
def filter_colleges(mhcet_percentile, jee_percentile, category):
    mhcet_query = "SELECT college_name, branch FROM colleges WHERE percentile <= ? AND seat_type = ?"
    jee_query = "SELECT college_name, branch FROM colleges WHERE percentile <= ? AND seat_type = 'AI'"    
    colleges = []
    distinct_branches = []
    try:
        with sqlite3.connect('data.db') as conn_data:
            c_data = conn_data.cursor()

            if jee_percentile:
                c_data.execute(jee_query, (jee_percentile,))
                colleges = c_data.fetchall()
                c_data.execute("SELECT DISTINCT branch FROM (" + jee_query + ")", (jee_percentile,))
                distinct_branches = c_data.fetchall()

            if mhcet_percentile:
                c_data.execute(mhcet_query, (mhcet_percentile, category))
                colleges = c_data.fetchall()
                c_data.execute("SELECT DISTINCT branch FROM (" + mhcet_query + ")", (mhcet_percentile, category))
                distinct_branches = c_data.fetchall()

            if mhcet_percentile is None and jee_percentile is None:
                raise ValueError("Both MHCET and JEE percentiles are None.")
    except sqlite3.Error as e:
        print("Error querying database:", e)
    return colleges, distinct_branches

if __name__ == '__main__':
    app.run(port=8000, debug=True)

