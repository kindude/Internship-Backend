import os
from dotenv import load_dotenv
# loading variables from .env
load_dotenv()
host = os.getenv("HOST")
port = os.getenv("PORT")
