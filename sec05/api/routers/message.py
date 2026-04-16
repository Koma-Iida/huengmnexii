from datetime import datetime
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

import api.schemas.message as message_schema

router = APIRouter()


@router.get("/messages", response_model=message_schema.Response)
async def get_messages(request: Request,
                       from_id: int | None = 1, to_id: int | None = None,
                       from_time: datetime | None = None,
                       important: bool | None = None,
                       ids_only: bool = False):
    """全ての message を返す"""
    if from_id is None or from_id < 1:
        from_id = 1
    if to_id is None:
        # to_id が指定されない場合は，現在の最大IDまで取得する．
        to_id = request.app.state.system.current_id
    l: list = []
    for i in range(from_id, to_id + 1):
        if i in request.app.state.system.messages:
            if from_time is None or \
               from_time <= request.app.state.system.messages[i].update_time:
                if important is None:
                    l.append(i)
                elif request.app.state.system.messages[i].important == important:
                    l.append(i)

    # ID のリストのみ返す
    if ids_only:
        return message_schema.Response(
            current_id=request.app.state.system.current_id,
            current_time=datetime.now(),
            ids=l)

    return message_schema.Response(
        current_id=request.app.state.system.current_id,
        current_time=datetime.now(),
        messages={i: request.app.state.system.messages[i] for i in l})


@router.get("/messages/current_id")
async def get_messages_current_id(request: Request):
    return {"current_id": request.app.state.system.current_id}


@router.post("/messages", response_model=message_schema.Message)
async def post_message(request: Request, message: message_schema.MessageBase):
    """message のPOST"""
    next_id = request.app.state.system.current_id + 1
    time = datetime.now()
    m = message_schema.Message(time=time, update_time=time, id=next_id,
                               **message.model_dump())
    request.app.state.system.messages[next_id] = m
    request.app.state.system.current_id = next_id
    return m


@router.get("/messages/{message_id}", response_model=message_schema.Message)
async def get_message(request: Request, message_id: int):
    """個別 message のGET"""
    # 該当 ID の message が存在しない場合は 404 を返す(他の関数でも同様)
    if message_id not in request.app.state.system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    return request.app.state.system.messages[message_id]


@router.put("/messages/{message_id}", response_model=message_schema.Message)
async def put_message(request: Request,
                      message_id: int, message: message_schema.MessageBase):
    """message のPUT"""
    if message_id not in request.app.state.system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    orig = request.app.state.system.messages[message_id]
    m = message_schema.Message(time=orig.time,
                               update_time=datetime.now(),
                               id=message_id,
                               **message.model_dump())
    request.app.state.system.messages[message_id] = m
    return m


@router.delete("/messages/{message_id}")
async def delete_message(request: Request, message_id: int):
    """message のDELETE"""
    if message_id not in request.app.state.system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    del request.app.state.system.messages[message_id]
    return {"success": True}


@router.get("/messages/{message_id}/important")
async def get_message_important(request: Request, message_id: int):
    """message important flag の GET """
    if message_id not in request.app.state.system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    return {"important": request.app.state.system.messages[message_id].important}


@router.put("/messages/{message_id}/important")
async def put_message_important(request: Request, message_id: int):
    """message important flag の PUT (important = True)"""
    if message_id not in request.app.state.system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    request.app.state.system.messages[message_id].update_time = datetime.now()
    request.app.state.system.messages[message_id].important = True
    return {"success": True}


@router.delete("/messages/{message_id}/important")
async def delete_message_important(request: Request, message_id: int):
    """message important flag の DELETE (important = False)"""
    if message_id not in request.app.state.system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    request.app.state.system.messages[message_id].update_time = datetime.now()
    request.app.state.system.messages[message_id].important = False
    return {"success": True}
