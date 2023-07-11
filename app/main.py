
import uvicorn
from fastapi import FastAPI
from ENV import host, port




app = FastAPI()


@app.get("/")
def main():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


if __name__ == '__main__':
    uvicorn.run(app, host, port)
