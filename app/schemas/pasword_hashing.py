import hashlib
import ENV


def hash(password) ->str:
    salt = str(ENV.salt)
    database_password = str(password) + salt
    hashed = hashlib.md5(database_password.encode()).hexdigest()
    return hashed