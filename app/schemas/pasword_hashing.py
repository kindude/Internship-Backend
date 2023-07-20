import hashlib
import os


def hash(password):
    salt = os.getenv("SALT")
    database_password = password + salt
    hashed = hashlib.md5(database_password.encode()).hexdigest()
    return hashed