import os
import random
import string
import requests
import batch_extract_requests
from time import sleep

# ==========================================
# CONFIGURATION
# ==========================================

# Generic target endpoint placeholder
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


def random_email(name):
    email_name = name.replace(" ", "").lower()
    domains = ["@gmail.com", "@hotmail.com", "@outlook.com", "@iitk.ac.in", "@symbiosis.org"]
    domain = random.choice(domains)
    number = random.randint(100, 9999)
    return f"{email_name}{number}{domain}"


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
    email = random_email(name)
    filename = referral_code
    browser_id = random_browser_id()
    password = random_password()
    
    cred = f"{email}:{password}\n"

    # Explicit UTF-8 encoding added for cross-platform file writing
    with open(f"{filename}.txt", "a", encoding="utf-8") as f:
        f.write(cred)

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
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

        if response.status_code != 200:
            print(f"❌ [ERROR {response.status_code}] Response Body:")
            print(response.text)
        else:
            print(f"✅ [SUCCESS {response.status_code}] Response Snippet:")
            print(response.text[:200])

    except requests.RequestException as e:
        print(f"❌ [NETWORK ERROR] | {e}")


# ==========================================
# MAIN
# ==========================================

def main():

    referral = input("Referral code: ").strip()

    try:
        count = int(input("Number of requests: "))
    except ValueError:
        print("Invalid number.")
        return

    if count <= 0:
        print("Number must be greater than 0.")
        return
    # STEP 1: Send initial requests
    print("\n>>> [1/3] Sending initial requests...")
    for i in range(count):
        sleep(random.randint(2, 5))
        send_request(referral)


        # STEP 2: Call batch_extract_requests on saved credentials file
    print("\n>>> [2/3] Extracting referral links & codes from created accounts...")
    accounts_file = f"{referral}.txt"
    if os.path.exists(accounts_file):
        batch_extract_requests.process_file(accounts_file)
    else:
        print(f"Notice: {accounts_file} file not found.")
        return

#     # STEP 3: Read newly extracted referral code from the file & send final requests
#     print("\n>>> [3/3] Sending final requests using extracted code...")

#     if os.path.exists(accounts_file ):
#         with open(accounts_file , "r", encoding="utf-8") as file:
#             refer = file.readline().strip()
#             if refer:
#                 parts = refer.split(":")
#                 refer = parts[-1]
#                 invite = random.randint(2, 5)
#                 for j in range(invite):
#                     sleep(random.randint(2, 5))
#                     send_request(refer)
#             else:
#                 print("Referral code not found in referral.txt")
#     else:
#         print("Notice: referral.txt file not found, skipping additional requests.")





    # STEP 3: Read extracted referral codes line-by-line and send final requests
    print(f"\n>>> [3/3] Sending final requests using all extracted codes...")
    if os.path.exists(accounts_file):
        with open(accounts_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(":")
                extracted_code = parts[-1]  # Gets the referral code from this line
                
                if extracted_code and not extracted_code.startswith("ERROR") and not extracted_code.startswith("LOGIN"):
                    print(f"[+] Processing extracted code: {extracted_code}")
                    invite_count = random.randint(2, 5)
                    print("Sending invite is"+ invite_count)
                    for j in range(invite_count):
                        sleep(random.randint(2, 5))
                        send_request(extracted_code)
    else:
        print(f"[-] Notice: {accounts_file} not found.")

if __name__ == "__main__":
    main()
