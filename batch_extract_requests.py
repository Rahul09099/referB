"""
Fast Batch Referral Link & Signup Code Extractor for KaamCash
--------------------------------------------------------------
Uses direct HTTP API requests and pure Python response decoding.
Appends BOTH the full share link AND the auto-filled signup referral code 
to each line in your accounts text file.

Output Format per line: `email:password:referral_link:signup_code`
Example:
  user@gmail.com:pass123:https://kaamcash.icks.top/pasia/4dAMXOn5:4dAMXO

Usage:
    python batch_extract_requests.py --file accounts.txt
"""

import os
import sys
import json
import base64
import argparse
import requests

# Ensure UTF-8 output on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

API_URL = "https://kaamcash.icks.top/api/init/98j"
BASE_INVITE_URL = "https://kaamcash.icks.top/pasia/"

def h1(e: str) -> bytes:
    """Decodes base64url string into bytes."""
    t = e.replace("-", "+").replace("_", "/")
    n = len(t) % 4
    if n > 0:
        t += "=" * (4 - n)
    return base64.b64decode(t)

def f1(t) -> int:
    """Converts key to int safely."""
    try:
        return int(t)
    except:
        return 0

def decode_skm_response(encoded_str: str, key_seed: int = 9) -> str:
    """Decodes compiled API responses from KaamCash."""
    try:
        n = h1(encoded_str)
        r = f1(key_seed)
        chars = []
        for l in range(len(n)):
            if l % 3 == 0:
                u = r % 2
            elif l % 3 == 1:
                u = r % 5
            else:
                u = r % 7
            chars.append(chr(n[l] + u))
        s = "".join(chars)
        a = base64.b64decode(s)
        return a.decode('utf-8', errors='ignore')
    except Exception as err:
        print(f"  [!] Decode Error: {err}")
        return ""

def get_referral_details(email: str, password: str) -> tuple:
    """Authenticates account via HTTP API and returns (referral_link, raw_signup_code)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://kaamcash.icks.top",
        "Referer": "https://kaamcash.icks.top/login"
    }

    payload = {
        "purpose": "auth.login",
        "ce": True,
        "payload": {
            "countryCode": "IN",
            "phone": email,
            "password": password
        }
    }

    try:
        res = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        
        if res.status_code != 200:
            print(f"  [-] Login failed (HTTP {res.status_code}): {res.text}")
            return "LOGIN_FAILED", "LOGIN_FAILED"

        decoded_text = decode_skm_response(res.text, key_seed=9)
        if not decoded_text:
            return "DECODE_FAILED", "DECODE_FAILED"

        data = json.loads(decoded_text)
        user_info = data.get("user", {})
        
        ref_code = user_info.get("referralCode") or ""
        public_suffix = user_info.get("languageProfilePublicId") or ""
        
        if ref_code:
            full_code = f"{ref_code}{public_suffix}"
            link = f"{BASE_INVITE_URL}{full_code}"
            # ref_code is the exact raw code filled in the signup form (e.g. 4dAMXO)
            return link, ref_code
        else:
            return "NO_REF_CODE", "NO_REF_CODE"

    except Exception as e:
        print(f"  [!] Request Error: {e}")
        return f"ERROR_{type(e).__name__}", f"ERROR_{type(e).__name__}"

def process_file(file_path: str, output_path: str = None, force: bool = False):
    if not os.path.exists(file_path):
        print(f"[-] File not found: {file_path}")
        return

    target_output = output_path if output_path else file_path

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    updated_lines = []

    for line in lines:
        parts = line.split(":")
        
        # If line already has email:password:link:code and not forcing re-fetch, skip
        if not force and len(parts) >= 4 and parts[2].startswith("http"):
            print(f"[*] Skipping {parts[0]} (already processed)")
            updated_lines.append(line)
            continue

        if len(parts) < 2:
            print(f"[-] Skipping invalid format line: {line}")
            updated_lines.append(line)
            continue

        email = parts[0].strip()
        password = parts[1].strip()

        print(f"[*] Processing account: {email}")
        invite_link, signup_code = get_referral_details(email, password)
        print(f"  [+] Share Link: {invite_link}")
        print(f"  [+] Pre-filled Signup Code: {signup_code}")

        new_line = f"{email}:{password}:{invite_link}:{signup_code}"
        updated_lines.append(new_line)

        # Save progress incrementally to output file
        with open(target_output, "w", encoding="utf-8") as f:
            f.write("\n".join(updated_lines) + "\n")

    print(f"\n[+] All accounts processed! Saved to: {target_output}")

HELP_DESCRIPTION = """
==============================================================================
    KaamCash Fast Referral Link & Signup Code Extractor (Pure HTTP Edition)
==============================================================================

DESCRIPTION:
  Automates login to KaamCash (https://kaamcash.icks.top) for multiple accounts
  and extracts BOTH the full share link AND the pre-filled signup referral code.

INPUT FILE FORMAT:
  A plain text file containing one account credential per line:
  
    email_or_phone:password
    
  Example (accounts.txt):
    user1@gmail.com:SecretPass123
    user2@gmail.com:MyPassword99

OUTPUT FILE FORMAT:
  Updates the file in-place (or writes to --output) with referral link and code:
  
    email_or_phone:password:referral_link:signup_code
    
  Example Output:
    user1@gmail.com:SecretPass123:https://kaamcash.icks.top/pasia/4dAMXOn5:4dAMXO

USAGE EXAMPLES:
  1. Standard Run (updates accounts.txt in-place):
     python batch_extract_requests.py --file accounts.txt

  2. Save results to a new output file:
     python batch_extract_requests.py --file accounts.txt --output results.txt

  3. Force re-checking of already processed lines:
     python batch_extract_requests.py --file accounts.txt --force

==============================================================================
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="batch_extract_requests.py",
        description=HELP_DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-f", "--file",
        required=True,
        metavar="PATH",
        help="Path to the input text file containing email:password per line."
    )
    
    parser.add_argument(
        "-o", "--output",
        required=False,
        metavar="PATH",
        help="Path to save the output file. If omitted, updates the input file in-place."
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-extraction for accounts that already have referral details attached."
    )

    args = parser.parse_args()
    process_file(args.file, output_path=args.output, force=args.force)
