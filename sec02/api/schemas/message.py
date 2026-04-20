from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    name: str | None = Field(None,
                             examples=["System"],
                             description="Message from")
    message: str | None = Field(None,
                                examples=["Default Message"],
                                description="Message body")
    priority: int = Field(0, examples=[5],
                          description="Message priority. "
                          "Higher value means high priority.")
    the_number_of_pizza_we_made_yesterday: int = Field(0,
                                                              examples=[10],
                                                              description='This is the number of pizza that we made yesterday.')
    


class Message(MessageBase):
    time: datetime | None = Field(None, 
                                  description="Message post time")
    
