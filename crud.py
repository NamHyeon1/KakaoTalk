from sqlalchemy.orm import Session
from models import User, Chats, Message, Friend
from schema import ChatSchema, UserSchema, MessageSchema, MesesageGetSchema, FriendSchema, ChatSchemaAdd, profileUpdateRequestSchema
from sqlalchemy import update

# 회원가입


def db_register_user(db: Session, id, password):

    db_item = User(id=id, password=password)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# 이미 회원가입한 사용자인지 확인
def db_get_isalreadyregistered(db: Session, id):

    res = db.query(User).filter(User.id == id).first()

    return res


# 로그인 한 유저 받아오기
def db_logined_user(db: Session, user: User):
    # print(user.id)
    return db.query(User).filter(User.id == user.id).all()


# 친구 list 받아오기
def db_get_friedns(db: Session, user: User):

    return db.query(Friend).filter(Friend.owner_id == user.id).all()


# 친구추가
def db_add_friends(db: Session, item: FriendSchema, user: User):

    friendData = db.query(User).filter(User.id == item.friendName).first()

    print(friendData)

    if not friendData:
        return "error"

    db_item = Friend(friend=item.friendName, owner_id=user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


# 채팅방 만들기
def db_create_chatting(db: Session, user: User, chatInfo: ChatSchemaAdd):

    temp = user.id + " " + chatInfo.friends

    print("attendances : " + temp)

    db_item = Chats(attendances=temp, lastmessage="", isgroup=chatInfo.isGroup)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


# 친구리스트페이지에서 채팅하기 클릭했을 때 채팅방이 이미 존재하는 채팅방인지 확인하는 용도
def db_get_chatting(db: Session, user: User, chatInfo: ChatSchema):

    temp = user.id + " " + chatInfo.friends

    result = db.query(Chats).filter(Chats.attendances.contains(user.id))    \
        .filter(Chats.attendances.contains(chatInfo.friends)).first()

    return result


# 채팅방에 참여한 사용자들 추가하기 (ex. 1번 채팅방 => 김남현 안성수)
# def db_add_chatusers(db: Session, username: str, chatid):

    print("add chatuser : " + username)

    db_item = ChatUsers(chat_id=chatid, userid=username)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


# 사용자가 포함된 채팅방 정보 불러오기
def db_get_chattingList(db: Session, user: User):

    result = db.query(Chats).filter(Chats.attendances.contains(user.id)).all()

    return result


# 메세지 추가하기
def db_add_message(db: Session, item: MessageSchema, user: User):
    db_item = Message(userid=user.id, content=item.content,
                      time=item.time, chatid=item.chatid, isImg=item.isImg)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db.query(Message).filter(Message.chatid == item.chatid).all()


# 메세지 받아오기 채팅방 아이디로 filtering해서 받아온다
def db_get_messages(db: Session, item: MesesageGetSchema):
    return db.query(Message).filter(Message.chatid == item.chatid).all()


# chatting 방의 가장 최근 메세지 정보 업데이트
def db_update_lastmessage(db: Session, chatid, messageContent):

    db.query(Chats).filter(Chats.chat_id == chatid).update(
        {Chats.lastmessage: messageContent})

    return


# 사용자 받아오기 (프로필 보여줄 때 클릭한 사용자가 누군지 보여주기 위함)
def db_get_user(db: Session, userid: str):
    return db.query(User).filter(User.id == userid).all()


# 사용자 프로필 update
def db_update_userProfile(db: Session, item: profileUpdateRequestSchema, user: User):

    # print("--------update profile----------")
    # print("유저 Id : " + user.id)
    # print("상태메세지 : " + item.statusmessage)
    # print("이미지 링크 : " + item.imageLink)

    res = db.query(User).filter(User.id == user.id).first()

    res.photo = item.imageLink
    res.statusMessage = item.statusmessage

    db.commit()

    return
