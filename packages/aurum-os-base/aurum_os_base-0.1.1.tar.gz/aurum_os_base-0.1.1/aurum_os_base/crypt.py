import argparse
import os
import getpass
from cryptography.fernet import Fernet

def check_permissions(file_path):
    try:
        # Check if the current user has read and write permissions for a file
        if os.access(file_path, os.R_OK | os.W_OK):
            return f"You have read and write permissions for '{file_path}'"
        else:
            return f"You do not have read and write permissions for '{file_path}'"
    except Exception as e:
        return f"Error checking permissions: {str(e)}"

def encrypt_text(text, encryption_key):
    try:
        f = Fernet(encryption_key)
        encrypted_text = f.encrypt(text.encode())
        return encrypted_text
    except Exception as e:
        return f"Encryption error: {str(e)}"

def decrypt_text(encrypted_text, encryption_key):
    try:
        f = Fernet(encryption_key)
        decrypted_text = f.decrypt(encrypted_text).decode()
        return decrypted_text
    except Exception as e:
        return f"Decryption error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Security Operations")
    parser.add_argument("--check-permissions", help="Check file permissions")
    parser.add_argument("--encrypt", nargs=2, metavar=("text", "key"), help="Encrypt text with a key")
    parser.add_argument("--decrypt", nargs=2, metavar=("encrypted_text", "key"), help="Decrypt text with a key")

    args = parser.parse_args()

    if args.check_permissions:
        result = check_permissions(args.check_permissions)
        print(result)

    if args.encrypt:
        text, key = args.encrypt
        encrypted_text = encrypt_text(text, key)
        print(f"Encrypted text: {encrypted_text}")

    if args.decrypt:
        encrypted_text, key = args.decrypt
        decrypted_text = decrypt_text(encrypted_text, key)
        print(f"Decrypted text: {decrypted_text}")

if __name__ == "__main__":
    main()

