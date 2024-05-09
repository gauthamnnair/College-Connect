from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key ='secertkey'

with sqlite3.connect('users.db') as conn:
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT NOT NULL UNIQUE,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL)''')

# Add login check decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

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

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Check if email is already registered
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            return "Email is already registered. Please use a different email."

        # Insert user data into the database
        c.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, hashed_password))

    # Redirect to login page after successful signup
    return redirect('/login')

# Render the login page
@app.route('/login', methods=['GET'])
def login_from():
    return render_template('login.html')

# Handle login form submission
@app.route('/login', methods=['POST'])
def login():
    # Extract form data
    username = request.form['loginUsername']
    password = request.form['loginPassword']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Authenticate user
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = c.fetchone()

    if user:
        # Set session variable to indicate user is logged in
        session['logged_in'] = True
        return redirect('/form')
    else:
        return redirect('/login')

# Render the form
@app.route('/form', methods=['GET'])
@login_required
def admission_form():
    return render_template('form.html', logged_in='logged_in' in session)

# Handle logout
@app.route('/logout', methods=['GET'])
def logout():
    # Clear the session
    session.clear()   
    # Redirect to the index page
    return redirect('/')

# Handle admission form submission
@app.route('/list', methods=['POST'])
def submit_admission():
    mhcet_percentile = request.form.get('mhcet_percentile')
    jee_percentile = request.form.get('jee_percentile')
    category = request.form.get('category') + 'S'  # Assuming category is concatenated with 'S'
    colleges, distinct_branches, chances = filter_colleges(mhcet_percentile, jee_percentile, category)

    # Pass data to the result.html template
    return render_template('result.html',
                            colleges=colleges, 
                            distinct_branches=distinct_branches, 
                            mhcet_percentile=mhcet_percentile,
                            jee_percentile=jee_percentile,
                            category=category,
                            get_college_website=get_college_website,
                            get_page_num=get_page_num,
                            chances= chances,
                            logged_in='logged_in' in session)

# Function to fetch colleges from the database
def filter_colleges(mhcet_percentile, jee_percentile, category):
    mhcet_query = "SELECT college_name, branch, percentile, 'MHCET', page_num FROM colleges WHERE percentile <= ? AND seat_type = ? LIMIT 150"
    jee_query = "SELECT college_name, branch, percentile, 'JEE', page_num FROM colleges WHERE percentile <= ? AND seat_type = 'AI' LIMIT 150"    
    colleges = []
    distinct_branches = []
    chances = []
    try:
        with sqlite3.connect('data.db') as conn_data:
            c_data = conn_data.cursor()
            if jee_percentile:
                c_data.execute(jee_query, (jee_percentile,))
                colleges += c_data.fetchall()

            if mhcet_percentile:
                c_data.execute(mhcet_query, (mhcet_percentile, category))
                colleges += c_data.fetchall()

            if mhcet_percentile is None and jee_percentile is None:
                raise ValueError("Both MHCET and JEE percentiles are None.")
            
            colleges.sort(key=lambda x: x[2] if x[2] else float('-inf'), reverse=True)  # Sorting based on percentile

            # Limit colleges to top 300
            colleges = colleges[:300]
            
            #Extracting distinct colleges
            for college in colleges:
                if college[1] not in distinct_branches:
                    distinct_branches.append(college[1])
           
            # Calculate chances and code
            for i, college in enumerate(colleges):
                college_name = college[0]                
                percentile = college[2]
                c_data.execute("SELECT code FROM details WHERE college_name=?", (college_name,))
                codes = c_data.fetchone()
                code = codes[0]
                if college[3] == 'JEE':
                    percentile_difference = abs(float(jee_percentile) - percentile)
                
                elif college[3] == 'MHCET':
                    percentile_difference = abs(float(mhcet_percentile) - percentile)

                if percentile_difference < 3:
                    chance = 'Probable'
                elif percentile_difference < 5:
                    chance = 'Fair Chance'
                else:
                    chance = 'Confirm'
                if chance not in chances:
                    chances.append(chance)

                # Convert tuple to list, append chance, then convert back to tuple
                college_list = list(college)
                college_list.append(chance)
                college_list.append(code)
                colleges[i] = tuple(college_list)

    except sqlite3.Error as e:
        print("Error querying database:", e)
    return colleges, distinct_branches,chances

def get_college_website(college_name):
    with sqlite3.connect('data.db') as conn_details:
        c_details = conn_details.cursor()
        c_details.execute("SELECT website_link FROM details WHERE college_name=?", (college_name,))
        website_link = c_details.fetchone()
        if website_link:
            return website_link[0]
        else:
            return "#"

def get_page_num(college_name, branch):
    with sqlite3.connect('data.db') as conn_details:
        c_details = conn_details.cursor()
        c_details.execute("SELECT page_num FROM colleges WHERE college_name=? AND branch=?", (college_name,branch))
        page_nums = c_details.fetchone()
        if page_nums:
            return f"https://fe2023.mahacet.org/2022/2022SeatMatrix.pdf#page={page_nums[0]}"
        else:
            return "#"

if __name__ == '__main__':
    app.run(port=8000, debug=True)

