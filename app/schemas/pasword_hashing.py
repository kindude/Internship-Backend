import hashlib
import ENV


def hash(password:str) ->str:
    salt = str(ENV.salt)
    database_password = str(password) + salt
    hashed = hashlib.md5(database_password.encode()).hexdigest()
    return hashed

def hash_with_salt(password: str) -> str:
    salt = str(ENV.salt)
    database_password = str(password) + salt
    # Use a secure hashing algorithm (SHA-256) instead of MD5
    hashed = hashlib.sha256(database_password.encode()).hexdigest()
    return hashed
