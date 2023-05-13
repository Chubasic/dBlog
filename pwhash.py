from passlib.hash import sha256_crypt

password = sha256_crypt.encrypt("password")
password2 = sha256_crypt.encrypt("password")
