from flask import Flask, request, redirect, render_template, session, url_for, flash, send_from_directory, abort
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Weak session handling
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')  # Ensure absolute path
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
with get_db_connection() as conn:
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    username TEXT UNIQUE, 
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
        cursor = conn.execute(f"SELECT filename FROM files WHERE owner = '{session['user']}'")  # SQL Injection risk
        files = [row['filename'] for row in cursor.fetchall()]
        conn.close()
    return render_template('index.html', files=files, user=session.get('user'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Plaintext password vulnerability
        conn = get_db_connection()
        try:
            conn.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")  # SQL Injection risk
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already taken.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")  # SQL Injection risk
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials.', 'danger')
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
    file.save(filepath)  # No file validation vulnerability
    
    conn = get_db_connection()
    conn.execute(f"INSERT INTO files (filename, owner) VALUES ('{filename}', '{session['user']}')")  # SQL Injection risk
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
        conn.execute(f"DELETE FROM files WHERE filename = '{filename}' AND owner = '{user}'")  # SQL Injection risk
        conn.commit()
        conn.close()
        flash('File deleted successfully.', 'success')
    else:
        flash('File not found.', 'danger')
    
    return redirect(url_for('index'))

@app.route('/uploads/<user>/<path:filename>')
def uploaded_file(user, filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user)
    file_path = os.path.join(user_folder, filename)
    if not os.path.exists(file_path):
        abort(404)  # Properly return 404 if file doesn't exist
    return send_from_directory(user_folder, filename)

@app.route('/get_file_preview/<user>/<filename>')
def get_file_preview(user, filename):
    extension = filename.split('.')[-1].lower()
    if extension in ['png', 'jpg', 'jpeg', 'gif']:
        return url_for('uploaded_file', user=user, filename=filename)
    elif extension in ['pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'xls', 'xlsx']:
        return '<a href="' + url_for('uploaded_file', user=user, filename=filename) + '" class="btn btn-primary">View</a>'
    else:
        return url_for('uploaded_file', user=user, filename=filename)  # Generic document icon
      
if __name__ == '__main__':
    app.run(debug=True)