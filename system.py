from flask import Flask, request, redirect, render_template, session, url_for, flash, send_from_directory, abort
import sqlite3
import os
import joblib
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Change this to a random secret key in production
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load phishing detection model
model = joblib.load("phishing_model.pkl")

def extract_features_from_url(url):
    features = {
        "URL_Length": len(url),
        "Have_IP": 1 if url.split("://")[-1][0].isdigit() else -1,
    }
    return pd.DataFrame([features])

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT UNIQUE, 
                    email TEXT UNIQUE,
                    password TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    filename TEXT, 
                    owner TEXT)''')
    conn.commit()

@app.route('/')
def index():
    files = []
    if 'user' in session:
        conn = get_db_connection()
        cursor = conn.execute(f"SELECT filename FROM files WHERE owner = '{session['user']}'")
        files = [row['filename'] for row in cursor.fetchall()]
        conn.close()
    return render_template('index.html', files=files, user=session.get('user'))

@app.route('/security_center', methods=['GET', 'POST'])
def security_center():
    result = None
    url_checked = None
    if request.method == 'POST':
        url_checked = request.form['url']
        features = extract_features_from_url(url_checked)
        prediction = model.predict(features)[0]
        result = "This link may be a phishing site!" if prediction == 1 else "This link appears safe."
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
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
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
                return render_template('warning.html', url=url)

        if session.get('failed_attempts', 0) >= 3:
            captcha_input = request.form.get('captcha', '')
            if captcha_input != session.get('captcha_answer'):
                flash("Captcha incorrect!", "danger")
                session['failed_attempts'] += 1
                return redirect(url_for('login'))

        conn = get_db_connection()
        cursor = conn.execute("SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?", (identifier, identifier, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = user['username']
            flash("Login successful!", "success")
            session['failed_attempts'] = 0
            session.pop('captcha_question', None)
            session.pop('captcha_answer', None)
            return redirect(url_for('index'))
        else:
            session['failed_attempts'] += 1
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

@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
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

    filename = secure_filename(file.filename)
    filepath = os.path.join(user_folder, filename)
    file.save(filepath)

    conn = get_db_connection()
    conn.execute(f"INSERT INTO files (filename, owner) VALUES ('{filename}', '{session['user']}')")
    conn.commit()
    conn.close()

    flash('File uploaded successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_file/<user>/<filename>', methods=['POST'])
def delete_file(user, filename):
    if 'user' not in session or session['user'] != user:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('index'))

    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user)
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        conn = get_db_connection()
        conn.execute(f"DELETE FROM files WHERE filename = '{filename}' AND owner = '{user}'")
        conn.commit()
        conn.close()
        flash('File deleted successfully!', 'success')
    else:
        flash('File not found.', 'danger')

    return redirect(url_for('index'))

@app.route('/uploads/<user>/<path:filename>')
def uploaded_file(user, filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user)
    file_path = os.path.join(user_folder, filename)
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory(user_folder, filename)

@app.route('/get_file_preview/<user>/<filename>')
def get_file_preview(user, filename):
    extension = filename.split('.')[-1].lower()
    if extension in ['png', 'jpg', 'jpeg', 'gif']:
        return url_for('uploaded_file', user=user, filename=filename)
    elif extension in ['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx']:
        return '<a href="' + url_for('uploaded_file', user=user, filename=filename) + '" class="btn btn-primary">View</a>'
    else:
        return url_for('uploaded_file', user=user, filename=filename)

@app.route('/verify_url', methods=['POST'])
def verify_url():
    url = request.form['url']
    features = extract_features_from_url(url)
    prediction = model.predict(features)[0]
    if prediction == 1:
        return render_template('warning.html', url=url)
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
