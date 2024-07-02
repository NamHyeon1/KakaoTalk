from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    # index = Column(Integer, primary_key=True)
    id = Column(String, primary_key=True)
    password = Column(String)
    photo = Column(String)
    statusMessage = Column(String)


class Friend(Base):
    __tablename__ = "friends"

    index = Column(Integer, primary_key=True)
    owner_id = Column(String)
    friend = Column(String)

# 톡방 아이디로 메세지를 연결


class Message(Base):
    __tablename__ = "messages"

    index = Column(Integer, primary_key=True)
    userid = Column(String)
    # reciever = Column(String)
    content = Column(String)
    time = Column(String)
    isImg = Column(Integer)
    chatid = Column(Integer, ForeignKey("chats.chat_id", ondelete="CASCADE"))


# chatlist 출력을 위해서
class Chats(Base):
    __tablename__ = "chats"
    chat_id = Column(Integer, primary_key=True)
    attendances = Column(String)  # 있는 채팅방인지 사용자들 이름으로 확인하기 위함
    lastmessage = Column(String)
    isgroup = Column(Integer)


# class ChatUsers(Base):
#     __tablename__ = "chatUsers"
#     index = Column(Integer, primary_key=True)
#     chat_id = Column(Integer, ForeignKey("chats.chat_id", ondelete="CASCADE"))
#     userid = Column(String)
