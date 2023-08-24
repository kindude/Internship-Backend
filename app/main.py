from typing import Annotated

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ENV import host, port
from fastapi.middleware.cors import CORSMiddleware

from routers.router_export import router_export
from  routers.routers_company import router_companies
from routers.routers_action import router_action
from routers.routers_user import router_user
from routers.router_quizzes import router_quiz

app = FastAPI()

origins = ["http://localhost:3000", "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["Content-Disposition"]
)


app.include_router(router_companies)
app.include_router(router_user)
app.include_router(router_action)
app.include_router(router_quiz)
app.include_router(router_export)



@app.api_route('/', methods=['GET', 'DELETE'])
def main():
    return {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


if __name__ == '__main__':
    uvicorn.run("main:app", host=host, port=port, reload=True)
