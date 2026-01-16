import bcrypt
import hashlib
from passlib.hash import pbkdf2_sha256
from cryptography.fernet import Fernet

# ask for a username and password
username = input("Enter username: ")
password = input("Enter password: ")

# hash the password using bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(f"\nbcrypt\n{hashed.decode('utf-8')}\n")

# password for use in htaccess files
htpasswd_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
print(f".htpasswd\n{username}:{htpasswd_password.decode('utf-8')}\n")

# hash the password using passlib's pbkdf2_sha256
hashed_pl = pbkdf2_sha256.hash(password)
print(f"passlib pbkdf2_sha256\n{hashed_pl}\n")

# hash the password using SHA3-256
sha3_hash = hashlib.sha3_256(password.encode('utf-8')).hexdigest()
print(f"SHA3-256\n{sha3_hash}\n")

# generate a random Fernet key for symmetric encryption
fernet_key = Fernet.generate_key()
print(f"Randomly Generated Fernet Key (symmetric encryption)\n{fernet_key.decode('utf-8')}\n")
