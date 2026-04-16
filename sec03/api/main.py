from datetime import datetime
import json

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import ValidationError

import api.schemas.message as message_schema


def load(app):
    try:
        with open("data.json", "rt", encoding="utf-8") as f:
            data_dict = json.load(f)
            app.state.message = message_schema.Message.model_validate(data_dict)
    except (FileNotFoundError, ValidationError):
        # ファイルが存在しない or ファイルがうまく読めない
        # →Default の Message を作成する
        app.state.message = message_schema.Message()


async def save(app):
    with open("data.json", "wt", encoding="utf-8") as f:
        f.write(app.state.message.model_dump_json(indent=4))


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


@app.get("/message", response_model=message_schema.Message)
async def get_message():
    return app.state.message


@app.post("/message", response_model=message_schema.Message)
async def post_message(message: message_schema.MessageBase):
    m = message_schema.Message(time=datetime.now(),
                               **message.model_dump())
    app.state.message = m
    return m
