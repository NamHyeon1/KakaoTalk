from pydantic import BaseModel
from typing import Optional

# 회원가입


class UserSchema(BaseModel):
    id: str
    password: str

    class Config:
        orm_mode = True


# chatting방 정보 back에 저장할 때
class ChatStatusUpdateSchema(BaseModel):
    chatid: Optional[int]

    class Config:
        orm_mode = True


# chatting방 만들 때
class ChatSchemaAdd(BaseModel):
    friends: Optional[str]
    number: Optional[int]
    isGroup: Optional[int]
    chatid: Optional[int]

    class Config:
        orm_mode = True


# chatting방 만들 때
class ChatSchema(BaseModel):
    friends: Optional[str]
    lastmessage: Optional[str]
    owner_id: Optional[str]
    owner: Optional[UserSchema]
    number: Optional[int]       # 참가자 수
    chatid: Optional[int]

    class Config:
        orm_mode = True


# 친구추가
class FriendSchema(BaseModel):
    friendName: Optional[str]

    class Config:
        orm_mode = True


class MesesageGetSchema(BaseModel):
    chatid: int

    class Config:
        orm_mode = True

# 메세지 추가


class MessageRequestBase(BaseModel):
    userid: str
    content: str
    time: str
    chatid: int
    isImg: int


class MessageRequestCreate(MessageRequestBase):
    pass


class MessageSchema(MessageRequestBase):
    index: Optional[int]

    class Config:
        orm_mode = True


class profileUserRequestSchema(BaseModel):
    userid: str

    class Config:
        orm_mode = True


class profileUpdateRequestSchema(BaseModel):

    imageLink: Optional[str]
    statusmessage: Optional[str]

    class Config:
        orm_mode = True


class imageUpdateSchema(BaseModel):

    imageLink: Optional[str]

    class Config:
        orm_mode = True
