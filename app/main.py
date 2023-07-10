import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv


# loading variables from .env
load_dotenv()

app = FastAPI()


@app.get("/")
def hello():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


if __name__ == '__main__':
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    uvicorn.run(app, host, port)
