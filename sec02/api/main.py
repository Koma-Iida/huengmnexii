from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import api.schemas.message as message_schema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_methods=['*'],
)

app.state.message = message_schema.Message()


@app.get("/message", response_model=message_schema.Message)
async def get_message():
    return app.state.message


@app.post("/message", response_model=message_schema.Message)
async def post_message(message: message_schema.MessageBase):
    app.state.message = message_schema.Message(time=datetime.now(),
                                         **message.model_dump())
    return app.state.message
