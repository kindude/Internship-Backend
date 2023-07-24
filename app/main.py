import uvicorn
from fastapi import FastAPI
from ENV import host, port
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["Content-Disposition"]
)


app.include_router(router)




@app.api_route('/', methods=['GET', 'DELETE'])

def main():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


if __name__ == '__main__':
    uvicorn.run("main:app", host=host, port=port, reload=True)
