from datetime import datetime
from pydantic import BaseModel, Field, Base64Bytes


class MessageBase(BaseModel):
    name: str | None = Field(None,
                             examples=["System"],
                             description="Message from")
    message: str | None = Field(None,
                                examples=["Default Message"],
                                description="Message body")
    image: Base64Bytes | None = Field(None, description="Image data")
    image_type: str | None = Field(None, description="Image MIME type")
    image_filename: str | None = Field(None,
                                       description="File name of image data")


class Message(MessageBase):
    time: datetime | None = Field(None, description="Message post time")
    
    
class Messages(BaseModel):
    messages: list[Message] = Field(default_factory=list, description="List of messages")