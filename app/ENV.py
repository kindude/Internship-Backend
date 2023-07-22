import os
from dotenv import load_dotenv
# loading variables from .env
load_dotenv()
host = os.getenv("HOST")
port = int(os.getenv("PORT", 8000))
salt = os.getenv("SALT")

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
postgres_ports = os.getenv("POSTGRES_PORTS")
postgres_db = os.getenv("POSTGRES_DB")
docker_db_name = os.getenv("DB_POSTGRES_DB_NAME")

DB_URL_CONNECT = "postgresql+asyncpg://" + user + ":" + password + "@" + docker_db_name + ":" + postgres_ports + "/" + postgres_db
