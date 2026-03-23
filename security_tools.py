# SECURITY TOOLS #

import base64
import hashlib
import secrets
import string

from cryptography.fernet import Fernet	# pip install cryptography to use Fernet.

# LITERAL SUBSTITUTIONS

KEY_LENGTH = 32		# Fernet requires a 32-byte key.
SALT_LENGTH = 16	# scrypt recommends a 16-byte salt or larger.

# FUNCTIONS

# Determines if password_1 and password_2 are equivalent.
def passwords_match(password_1, password_2):
	return password_1 == password_2

# Generates a random string length characters long, chosen from the alphabet specified by letters, digits, and punctuation.
# Uses the most secure randomization function available to the OS.
def secure_random_string(length, letters=1, digits=1, punctuation=1):
	alphabet = ""

	if (letters):
		alphabet = string.ascii_letters
	
	if (digits):
		alphabet += string.digits

	if (punctuation):
		alphabet += string.punctuation

	secure_random_string = ""

	for i in range(length):
		secure_random_string += secrets.choice(alphabet)
	
	return secure_random_string

# Generates a SHA256 hash from plaintext and salt.
def salted_hash(plaintext, salt):
	return hashlib.sha256((salt + plaintext).encode()).hexdigest()

# Generates a key of length bytes from password and salt using the scrypt key derivation function.
def derived_key(password, salt, length=KEY_LENGTH):
	b_password = bytes(password, encoding="utf-8")
	b_salt = bytes(salt, encoding="utf-8")
	key = hashlib.scrypt(b_password, salt=b_salt, n=2, r=8, p=1, dklen=length)	# what work factors make sense in this context?

	return key

# Creates a Fernet token string (a symmetric cipher) from plaintext and 32-byte key.
def encrypt(plaintext, key):
	b64_key = base64.b64encode(key)
	fernet_encrypter = Fernet(b64_key)
	b_plaintext = bytes(plaintext, encoding="utf-8")
	fernet_token = fernet_encrypter.encrypt(b_plaintext)

	return str(fernet_token, encoding="utf-8")

# Deciphers a Fernet token string (a symmetric cipher) from cipher and 32-byte key.
def decrypt(cipher, key):
	b64_key = base64.b64encode(key)
	fernet_decrypter = Fernet(b64_key)
	plaintext = str(fernet_decrypter.decrypt(cipher), encoding="utf-8")

	return plaintext
