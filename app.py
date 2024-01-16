import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, send_file, jsonify
import csv
from random import randint
import qrcode
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)
# For simplicity, we'll use an in-memory list as a placeholder for a database - this will be replaced with a DBMS solution at a later stage of development but for now, this works just fine.
main_table = []
admin_list = [
    {"admin1": "password1"},
    {"admin2": "password2"},
    # Add more admins as needed
]

user_list = [
    # Add more users as needed
]

# Index constants for user data
USER_ID_INDEX = 0
NAME_INDEX = 1
EMAIL_INDEX = 2
MOBILE_INDEX = 3
USERNAME_INDEX = 4
PASSWORD_INDEX = 5
COUPON_INDEX = 6  # New index for food coupons
SESSION_ATTENDANCE_FOLDER = 'session_attendance'
ALLOWED_EXTENSIONS = {'csv'}

app.config['SESSION_ATTENDANCE_FOLDER'] = SESSION_ATTENDANCE_FOLDER

# Function to save user data to a CSV file
def save_user_data():
    with open('user_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for user in user_list:
            writer.writerow(user)


# Call this function after adding a new user
# Example: save_user_data()

# Function to load user data from a CSV file
def load_user_data():
    try:
        with open('user_data.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                user_list.append(row)
    except FileNotFoundError:
        # Handle the case where the file doesn't exist
        pass

# Call this function at the beginning of your script
# Example: load_user_data()
load_user_data()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_table')
def admin_table():

    # Generate data for the main table
    table_data = []
    for index, user in enumerate(user_list):
        # Add more data for each row in the table
        table_data.append({
            'id': index + 1,
            'user_id': user[0],
            'name': user[1],
            'email': user[2],
            'mobile': user[3],
            'username': user[4],
            'password': user[5],
            'coupons_remaining': user[6]  # Placeholder for coupons remaining, update as needed
        })

    # Pass the data to the template
    return render_template('admin_table.html', table_data=table_data)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists in the admin list
        for admin in admin_list:
            if username in admin:
                # Check if the entered password matches the stored password
                if admin[username] == password:
                    # Redirect to the admin_dashboard page
                    session['username'] = username
                    session['password'] = password
                    return render_template('admin_dashboard.html')

    # If username or password is incorrect, refresh the page
    return render_template('admin_login.html')


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match any user in the user_list
        for user in user_list:
            if username == user[4] and password == user[5]:
                # Store the username and user ID in the session to track the logged-in user
                session['username'] = username
                session['user_id'] = user[0]
                session['name'] = user[1]
                session['foodcoups'] = user[6]
                return redirect(url_for('user_dashboard'))

    return render_template('user_login.html')

@app.route('/user_dashboard')
def user_dashboard():
    # Retrieve the currently logged-in user from the session
    username = session.get('username', None)
    user_id = session.get('user_id', None)
    name = session.get('name', None)
    foodcoups = session.get('foodcoups', None)

    # Redirect to user_login if no user is logged in
    if not username:
        return redirect(url_for('user_login'))

    # Generate a QR code for the user's userID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(user_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save('static/qrcode.png')  # Save the image temporarily

    # Render the user_dashboard.html page with the logged-in user and QR code
    return render_template('user_dashboard.html', username=username, user_id=user_id, name=name, foodcoups = foodcoups)

@app.route('/forbidden')
def forbidden():
    return render_template('forbidden.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    # Check if the user is logged in
    if 'username' not in session:
        return redirect(url_for('index'))

    # Check if the logged-in user is an admin
    username = session['username']
    password = session.get('password')
    
    is_admin = any(username in admin and admin[username] == password for admin in admin_list)

    # Check if the user is an admin
    if not is_admin:
        return(redirect(url_for('forbidden')))  # Forbidden

    # Fetch data for the admin dashboard
    table_data = []
    for index, item in enumerate(main_table):
        # Generate URLs for the images
        image_url = url_for('uploaded_file', filename=item['image'])
        
        # Add more data for each row in the table
        table_data.append({
            'id': index + 1,
            'image': f'<img src="{image_url}" alt="Image" style="max-width: 100px; max-height: 100px;">',
            'problem_title': item['problem_title'],
            'severity': item['severity'],
            'location': item['location'],
            'reporter': item['reporter']
        })


    # Render the admin dashboard
    return render_template('admin_dashboard.html', table_data=table_data, username=username)

# Function to initialize a new user with default values
def initialize_new_user(name, email, mobile, username, password):
    user_id = str(randint(100000, 999999))
    return [user_id, name, email, mobile, username, password, 5]  # Default to 5 food coupons

@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        username = request.form['username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if the passwords match
        if new_password != confirm_password:
            return render_template('user_signup.html', message='Passwords do not match.')

        # Check if the username is already taken (case-insensitive)
        if any(user[USERNAME_INDEX].lower() == username.lower() for user in user_list):
            return render_template('user_signup.html', message='Username already taken. Please choose another.')

        # If username is available, add the new user to the user_list
        new_user = initialize_new_user(name, email, mobile, username, new_password)
        user_list.append(new_user)

        # Save the updated user_list to the CSV file
        save_user_data()

        # Redirect to user_login page after successful signup
        return redirect(url_for('user_login'))

    return render_template('user_signup.html', message=None)

# Import necessary libraries

# Import necessary libraries

# ... (previous code)

@app.route('/mark_attendance')
def mark_attendance():
    # Check if the user is an admin
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']
    password = session.get('password')
    is_admin = any(username in admin and admin[username] == password for admin in admin_list)

    if not is_admin:
        return redirect(url_for('forbidden'))  # Redirect to forbidden page

    # Implement the logic to mark attendance here
    return render_template('mark_attendance.html')  # You can create a new HTML template for this

@app.route('/manage_food_coupons')
def manage_food_coupons():
    # Check if the user is an admin
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']
    password = session.get('password')
    is_admin = any(username in admin and admin[username] == password for admin in admin_list)

    if not is_admin:
        return redirect(url_for('forbidden'))  # Redirect to forbidden page

    # Implement the logic to manage food coupons here
    return render_template('manage_food_coupons.html')  # You can create a new HTML template for this

@app.route('/logout')
def logout():
    # Clear any session variables related to user login
    session.pop('username', None)  # Assuming 'username' is the session key for the logged-in user
    # You may need to clear other session variables as well
    session.pop('password', None)
    session.pop('user_id', None)
    session.pop('name', None)
    session.pop('foodcoups', None)
    # Redirect to the homepage or login page
    return redirect(url_for('index'))  # Change 'index' to the actual route of your homepage or login page

@app.route('/decrement_coupon/<user_id>')
def decrement_coupon(user_id):
    # Find the user with the given user_id
    user = next((u for u in user_list if u[USER_ID_INDEX] == user_id), None)

    if user:
        # Check if coupons are available
        coupons_remaining = int(user[COUPON_INDEX])
        if coupons_remaining > 0:
            # Decrement the coupon count
            user[COUPON_INDEX] = str(coupons_remaining - 1)
            # Save the updated user_list to the CSV file
            save_user_data()
        return jsonify({'user_id': user_id, 'coupons_remaining': max(0, coupons_remaining - 1)})
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/start_session/<session_name>', methods=['POST'])
def start_session(session_name):
    session_file_path = os.path.join(app.config['SESSION_ATTENDANCE_FOLDER'], f'{session_name}.csv')

    if not os.path.exists(session_file_path):
        with open(session_file_path, 'w', newline='') as session_file:
            # Write a header to the CSV file
            csv_writer = csv.writer(session_file)
            csv_writer.writerow(['User ID'])

        return jsonify({'message': 'Session started successfully'}), 200
    else:
        return jsonify({'error': 'Session with the same name already exists'}), 400

@app.route('/update_session/<session_name>/<user_id>', methods=['POST'])
def update_session(session_name, user_id):
    session_file_path = os.path.join(app.config['SESSION_ATTENDANCE_FOLDER'], f'{session_name}.csv')

    if os.path.exists(session_file_path):
        # Check if the user ID already exists in the CSV file
        if not user_id_exists(session_file_path, user_id):
            with open(session_file_path, 'a', newline='') as session_file:
                # Append the user ID to the CSV file
                csv_writer = csv.writer(session_file)
                csv_writer.writerow([user_id])

            return jsonify({'message': f'User {user_id} marked as present in session "{session_name}"'}), 200
        else:
            return jsonify({'message': f'User {user_id} already marked as present in session "{session_name}"'}), 200
    else:
        return jsonify({'error': f'Session "{session_name}" does not exist'}), 404

def user_id_exists(session_file_path, user_id):
    # Check if the user ID already exists in the CSV file
    with open(session_file_path, 'r', newline='') as session_file:
        csv_reader = csv.reader(session_file)
        for row in csv_reader:
            if row and row[0] == user_id:
                return True
    return False

if __name__ == '__main__':
    app.run(debug=True)