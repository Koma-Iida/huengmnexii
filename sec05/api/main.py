import json

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

import api.schemas.message as message_schema
from api.routers import message


def load(app):
    try:
        with open("data.json", "rt", encoding="utf-8") as f:
            data_dict = json.load(f)
            app.state.system = message_schema.System.model_validate(data_dict)
    except (FileNotFoundError, ValidationError):
        # ファイルが存在しない or ファイルがうまく読めない
        # →Default の Message を作成する
        app.state.system = message_schema.System()

    app.state.counter = 0
    if len(app.state.system.messages) != 0:
        # id の最大値 + 1 をカウンタにセット
        app.state.counter = max(app.state.system.messages.keys()) + 1


async def save(app):
    with open("data.json", "wt", encoding="utf-8") as f:
        f.write(app.state.system.model_dump_json(indent=4))


@asynccontextmanager
async def lifespan(app: FastAPI):
    load(app)
    yield
    await save(app)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_methods=['*'],
)


@app.get("/", response_class=HTMLResponse)
async def get_client():
    """Return client HTML"""
    data = ''
    with open('client.html', 'rt', encoding='utf-8') as f:
        data = f.read()
    return data


app.include_router(message.router)
