from datetime import datetime
import json

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi import HTTPException
from pydantic import ValidationError

import api.schemas.message as message_schema


def load(app):
    try:
        with open("data.json", "rt", encoding="utf-8") as f:
            data_dict = json.load(f)
            app.state.messages = message_schema.Messages.model_validate(data_dict)
    except (FileNotFoundError, ValidationError):
        # ファイルが存在しない or ファイルがうまく読めない
        # →Default の Message を作成する
        app.state.messages = message_schema.Messages()


async def save(app):
    with open("data.json", "wt", encoding="utf-8") as f:
        f.write(app.state.messages.model_dump_json(indent=4))


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
async def get_client(request: Request):
    """Return client HTML"""
    data = ''
    with open('client.html', 'rt', encoding='utf-8') as f:
        data = f.read()
    server_ip, port = request.scope.get("server")
    data = data.replace("127.0.0.1:8000", f"{server_ip}:{port}")
    return data


@app.get("/message", response_model=message_schema.Messages)
async def get_message():
    return app.state.messages


@app.get("/message/{index}", response_model=message_schema.Messages)
async def get_message(index: int):
    message_list = app.state.messages.messages
    if index < 0 or index >= len(message_list):
        raise HTTPException(status_code=404, detail="Message not found")
    return message_schema.Messages(messages=[message_list[index]])


@app.post("/message", response_model=message_schema.Message)
async def post_message(message: message_schema.MessageBase):
    m = message_schema.Message(time=datetime.now(),
                               **message.model_dump())
    app.state.messages.messages.append(m)
    return m
