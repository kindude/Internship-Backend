import hashlib
import ENV

def hash_with_salt(password: str) -> str:
    database_password = str(password) + ENV.salt
    hashed = hashlib.sha256(database_password.encode()).hexdigest()
    return hashed
