import random
import string
import requests
from time import sleep
import os

# ==========================================
# CONFIGURATION
# ==========================================

TARGET = "https://kaamcash.icks.top/api/init/98j"

# ==========================================
# RANDOM DATA GENERATORS
# ==========================================

def random_name():
    consonants = "bcdfghjklmnpqrstvwxyz"
    vowels = "aeiou"

    def make_word():
        word = random.choice(consonants).upper()

        for _ in range(random.randint(2, 4)):
            word += random.choice(vowels + consonants)

        return word

    return f"{make_word()} {make_word()}"


def random_email():
    name = random_name().replace(" ", "").lower()
    number = random.randint(100, 9999)

    return f"{name}{number}@example.com"


def random_browser_id():
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(6))


def random_password():
    chars = string.ascii_letters + string.digits
    return "Test@" + "".join(random.choice(chars) for _ in range(10))


# ==========================================
# SEND TEST REQUEST
# ==========================================

def send_request(referral_code):

    name = random_name()

    # Use the same generated name for the email
    email_name = name.replace(" ", "").lower()
    email = f"{email_name}{random.randint(100, 9999)}@example.com"
    filename=referral_code
    browser_id = random_browser_id()
    password = random_password()
    cred=email+":"+password
    with open(f"{filename}.txt", "a") as f:
        f.write(cred)
        f.write("\n")
    payload = {
        "purpose": "auth.register",
        "ce": True,
        "payload": {
            "countryCode": "+91",
            "phone": email,
            "name": name,
            "password": password,
            "referralCode": referral_code,
            "languageProfileId": 2,
            "browserId": browser_id
        }
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            TARGET,
            json=payload,
            headers=headers,
            timeout=15
        )

        try:
            data = response.json()
            message = data.get("message", "No message")
        except ValueError:
            message = response.text[:200]

        # Only show status code + message
        print(f"{response.status_code} | {message}")

    except requests.RequestException as e:
        print(f"ERROR | {e}")


# ==========================================
# MAIN
# ==========================================

def main():

    referral = input("Referral code:").strip()

    try:
        count = int(input("Number of test requests (Don't exceed max is 9-10.): "))
    except ValueError:
        print("Invalid number.")
        return

    if count <= 0:
        print("Number must be greater than 0.")
        return

    for i in range(count):
        sleep(random.randint(2, 5))
        send_request(referral)
    if os.path.exists("referral.txt"):
        with open("referral.txt", "r") as file:
            refer=file.readline().strip()
            invite=random.randint(2,5)
            for j in range(invite):
                sleep(random.randint(2, 5))
                send_request(refer)
    else:
        print("Notice: referral.txt file not found, skipping additional requests.")

if __name__ == "__main__":
    main()
