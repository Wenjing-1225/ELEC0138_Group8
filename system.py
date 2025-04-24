from flask import Flask, request, redirect, render_template, session, url_for, flash, send_from_directory, abort
import sqlite3
import os
import joblib
import pandas as pd
import uuid
import hashlib
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Change this to a random secret key in production
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

root_dir = os.path.dirname(os.path.abspath(__file__))
model_dir = os.path.join(root_dir, "phishing_model.pkl")
feature_dir =  os.path.join(root_dir, "feature_columns.txt")
logging_dir = os.path.join(root_dir, "access_log")
# Load phishing detection model
model = joblib.load(model_dir)

logging.basicConfig(filename=logging_dir, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with open(feature_dir, "r") as f:
    feature_columns = [line.strip() for line in f.readlines()]

def extract_features_from_url(url: str): 
    """
    Features matching the trained model structure are extracted. 
    Fields that cannot be inferred from the URL are filled with default values ​​(0).
    """
    
    features = {
    'having_IP_Address': 1 if url.split("://")[-1][0].isdigit() else -1,
    'URL_Length': len(url),
    'Shortining_Service': -1 if "bit.ly" in url or "tinyurl" in url else 1,
    'having_At_Symbol': -1 if "@" in url else 1,
    'double_slash_redirecting': -1 if url.count("//") > 1 else 1,
    'Prefix_Suffix': -1 if "-" in url else 1,
    'having_Sub_Domain': -1 if url.count(".") > 2 else 1,
    'HTTPS_token': -1 if "https" not in url else 1
}

    # Extracting other features
    final_features = {col: features.get(col, 0) for col in feature_columns}
    return pd.DataFrame([final_features])
    
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
with get_db_connection() as conn:
    conn.execute('''Create table if not exists users (
                    id integer primary key autoincrement, 
                    username text unique, 
                    email text unique,
                    password text)''')
    conn.execute('''Create table if not exists files (
                    id integer primary key autoincrement, 
                    filename text,
                    original_filename text, 
                    owner text)''')
    conn.commit()

@app.route('/')
def index():
    files = []
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.execute(f"SELECT filename, original_filename FROM files WHERE owner = '{session['user']}'")
        for row in cursor.fetchall():
            file_info = {
                'secure_name': row['filename'],          # The randomized name shown on the link
                'original_name': row['original_filename']  # The name shown on preview
            }
            files.append(file_info)
        conn.close()
        logging.info(f"User {session['user']} accessed index page with {len(files)} files")
    else:
        logging.info("Anonymous user accessed index page")
    return render_template('index.html', files=files, user=session.get('user'))

@app.route('/security_center', methods=['GET', 'POST'])
def security_center():
    result = None
    url_checked = None

    if request.method == 'POST':
        url_checked = request.form['url']
        features = extract_features_from_url(url_checked)

        # Output the features used for prediction
        proba = model.predict_proba(features)[0]
        phishing_score = proba[1]

        print("Features used for prediction:")
        print(features)
        print(f"Phishing Probability Score: {phishing_score:.4f}")

        logging.info(f"User submitted URL for analysis: {url_checked} - Phishing score: {phishing_score:.4f}")

        # Determine the result based on the phishing score
        if phishing_score >= 0.9:
            result = f"High risk phishing site!"
        elif phishing_score >= 0.5:
            result = f"Suspicious site."
        else:
            result = f"This site appears safe."

    return render_template('security_center.html', result=result, url=url_checked)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            logging.info(f"New user registered: {username}")
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            logging.warning(f"Registration failed (duplicate): {username} / {email}")
            flash('Username or email already taken.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'failed_attempts' not in session:
        session['failed_attempts'] = 0

    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        url = request.form.get('url')

        if url:
            features = extract_features_from_url(url)
            prediction = model.predict(features)[0]
            if prediction == 1:
                logging.warning(f"Phishing detected in login URL: {url}")
                return render_template('warning.html', url=url)

        if session.get('failed_attempts', 0) >= 3:
            captcha_input = request.form.get('captcha', '')
            if captcha_input != session.get('captcha_answer'):
                logging.warning(f"Failed CAPTCHA for user: {identifier}")
                flash("Captcha incorrect!", "danger")
                session['failed_attempts'] += 1
                return redirect(url_for('login'))

        conn = get_db_connection()
        cursor = conn.execute("SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?", (identifier, identifier, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = user['username']
            logging.info(f"User logged in: {user['username']}")
            flash("Login successful!", "success")
            session['failed_attempts'] = 0
            session.pop('captcha_question', None)
            session.pop('captcha_answer', None)
            return redirect(url_for('index'))
        else:
            session['failed_attempts'] += 1
            logging.warning(f"Failed login attempt for: {identifier}")
            flash("Login failed, username/email or password incorrect!", "danger")
            if session['failed_attempts'] >= 3 and 'captcha_question' not in session:
                import random
                a = random.randint(1, 9)
                b = random.randint(1, 9)
                session['captcha_question'] = f"{a} + {b} = ?"
                session['captcha_answer'] = str(a + b)
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

def hashed_filename(original_filename):
    """Generate a secure, unpredictable filename while preserving the extension"""

    _, ext = os.path.splitext(original_filename) # Get file extension

    # Generate a UUID for random filename
    random_name = str(uuid.uuid4())

    # Create a hash for additional security
    hash_obj = hashlib.sha256(random_name.encode())
    return hash_obj.hexdigest() + ext

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        logging.warning(f"Unauthorized file upload attempt")
        flash('You must be logged in to upload files.', 'danger')
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file part.', 'danger')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file.', 'danger')
        return redirect(url_for('index'))

    username = session['user']
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], username)
    os.makedirs(user_folder, exist_ok=True)

    original_filename = secure_filename(file.filename)
    secure_name = hashed_filename(original_filename)

    filepath = os.path.join(user_folder, secure_name)
    file.save(filepath)

    conn = get_db_connection()
    conn.execute("INSERT INTO files (filename, original_filename, owner) VALUES (?, ?, ?)", (secure_name, original_filename, session['user']))
    conn.commit()
    conn.close()

    logging.info(f"User {username} uploaded file: {original_filename} as {secure_name}")

    flash('File uploaded successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(user, filename):
    if 'user' not in session or session['user'] != user:
        logging.warning(f"Unauthorized delete attempt by unknown user")
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('index'))

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], session['user'])
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        conn = get_db_connection()
        conn.execute(f"DELETE FROM files WHERE filename = '{filename}' AND owner = '{user}'")
        conn.commit()
        conn.close()
        logging.info(f"User {session['user']} deleted file: {filename}")
        flash('File deleted successfully!', 'success')
    else:
        logging.warning(f"User {session['user']} attempted to delete nonexistent file: {filename}")
        flash('File not found.', 'danger')

    return redirect(url_for('index'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):

    # Check if user is logged in
    if 'user' not in session:
        logging.warning(f"Unauthorized Access attempt to {filename}")
        abort(403)  # Unauthorized

    current_user = session['user']
    
    # Check if the user has access to this file
    conn = get_db_connection()
    cursor = conn.execute(f"SELECT * FROM files WHERE filename = '{filename}'")
    file_info = cursor.fetchone()
    conn.close()
    
    if not file_info:
        logging.info(f"User {current_user} atempted to access non-existent file")
        abort(404)  # File not found

    # Only the owner can access their secure files
    if file_info['owner'] != current_user:
        logging.info(f"User {current_user} atempted to access unauthorized file")
        abort(403)  # Access denied
    
    logging.info(f"User {current_user} accessed file: {filename}")

    # Find the owner's secure folder
    owner_folder = os.path.join(app.config['UPLOAD_FOLDER'], file_info['owner'])
    
    # Verify file exists
    file_path = os.path.join(owner_folder, filename)
    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(owner_folder, filename)

@app.route('/get_file_preview/<filename>')
def get_file_preview(filename):

    if 'user' not in session:
        logging.warning(f"Preview access attempt without login by unknown user")
        abort(403)

    extension = filename.split('.')[-1].lower()
    if extension in ['png', 'jpg', 'jpeg', 'gif']:
        return url_for('uploaded_file', filename=filename)
    elif extension in ['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx']:
        return '<a href="' + url_for('uploaded_file', filename=filename) + '" class="btn btn-primary">View</a>'
    else:
        return url_for('uploaded_file', filename=filename)

@app.route('/verify_url', methods=['POST'])
def verify_url():
    url = request.form['url']
    features = extract_features_from_url(url)
    prediction = model.predict(features)[0]
    if prediction == 1:
        logging.warning(f"Phishing link detected: {url}")
        return render_template('warning.html', url=url)
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
