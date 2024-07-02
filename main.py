from fastapi import FastAPI, WebSocket, Request, Depends, Response, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.logger import logger
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

from typing import List

from models import Base, User
from database import SessionLocal, engine
from crud import db_register_user, db_logined_user, db_create_chatting, db_get_chatting, db_get_chattingList, db_add_message, db_get_messages

from crud import db_get_friedns, db_add_friends, db_update_lastmessage, db_get_isalreadyregistered, db_get_user, db_update_userProfile

from schema import ChatSchemaAdd, MessageSchema, MessageRequestCreate, MesesageGetSchema, FriendSchema, ChatStatusUpdateSchema, profileUserRequestSchema, profileUpdateRequestSchema, imageUpdateSchema

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

Base.metadata.create_all(bind=engine)
app = FastAPI()
templates = Jinja2Templates(directory="templates")


class NotAuthenticatedException(Exception):
    pass


SECRET = "secret"

manager = LoginManager(SECRET, '/login', use_cookie=True)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")


now_chatting_id = {
    "chatid": 0,
    "userId": "",
    "imgLink": ""
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url='/login')


# 로그인 처리
@app.post('/token')
def login(response: Response, data: OAuth2PasswordRequestForm = Depends()):

    username = data.username
    password = data.password

    # db에서 있는 사용자인지 확인하고 쿠키추가하기
    user = get_user(username)

    if not user:
        raise InvalidCredentialsException
    if user.password != password:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data={'sub': username}
    )

    manager.set_cookie(response, access_token)

    return {'access_token': access_token}


# 로그아웃 처리
@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(key="access-token")
    return response


# db에서 있는 사용자인지 받아오기
@manager.user_loader()
def get_user(username: str, db: Session = None):
    if not db:
        with SessionLocal() as db:
            return db.query(User).filter(User.id == username).first()
    return db.query(User).filter(User.id == username).first()


# 로그인 페이지 불러오기
@app.get("/login")
async def client(request: Request):
    # /templates/client.html파일을response함
    dictionary = {
        "id": "Can You See me?"
    }
    return FileResponse("login.html", headers=dictionary)


# 회원가입 페이지 불러오기
@app.get("/registerpage")
def get_register():
    return FileResponse('register.html')


# 회원가입 처리
@app.post('/register')
def register_user(response: Response,
                  data: OAuth2PasswordRequestForm = Depends(),
                  db: Session = Depends(get_db)):

    # data 받아서 이미 있는 사용자인지 확인

    userid = data.username
    password = data.password

    res = db_get_isalreadyregistered(db, userid)

    # 없으면 생성하기

    if not res:
        user = db_register_user(db, userid, password)

        if user:
            return "User created"

        else:
            return "Failed"

    else:
        raise Exception("이미 존재하는 사용자")


# friendlist page 불러오기
@app.get('/friendlist')
def return_friendlistpage():
    return FileResponse('FriendList.html')


# friendlist page에서 현재 사용자 정보 받아오는 함수
@app.get('/getLoginUser')
def get_loginedUser(db: Session = Depends(get_db),
                    user=Depends(manager)):

    return db_logined_user(db, user)


# 친구추가 페이지 불러오기
@app.get('/addFriendPage')
def get_addFriendPage():

    return FileResponse("AddFriend.html")


# 친구들 리스트 불러오기
@app.get('/getFriendList')
def get_Friends(db: Session = Depends(get_db),
                user=Depends(manager)):

    return db_get_friedns(db, user)


# 친구 추가하는 함수
@app.post('/addFriend')
def add_friend(friendInfo: FriendSchema,
               db: Session = Depends(get_db),
               user=Depends(manager)):

    res = db_add_friends(db, friendInfo, user)

    if res == "error":
        # print("error")
        raise Exception("없는 사용자입니다.")

    return res

# 채팅방 생성하기


@app.post('/createChatRoom')
def post_createChatRoom(chatInfo: ChatSchemaAdd,
                        db: Session = Depends(get_db),
                        user=Depends(manager)):

    # 개인톡은 버튼을 처음 클릭했을 때 채팅방을 생성하고 채팅방을 들어가야하는데
    # 두번째부터는 이미 만들어진 채팅방을 불러오기만 하면되기에 아래처럼 db_get_chatting한 결과가 존재하면 해당 채팅방 정보를 서버에 저장하도록 구현하였다.
    # 단톡은 이미 만들어진 채팅방을 클릭하여 들어가기에 필터링을 하지 않았다.

    userNum = chatInfo.number  # 참가자 수

    result = None

    if (userNum != 2):

        result = db_create_chatting(db, user, chatInfo)

        users = chatInfo.friends.split(' ')

        print(users)

        # db_add_chatusers(db, user.id, result.chat_id)

        for friend in users:
            if friend == '':
                continue

            # db_add_chatusers(db, friend, result.chat_id)
    else:

        # 이미 존재하는 채팅방인지 확인
        result = db_get_chatting(db, user, chatInfo)

        if not result:
            result = db_create_chatting(db, user, chatInfo)

            # db_add_chatusers(db, user.id, result.chat_id)
            # db_add_chatusers(db, chatInfo.friends, result.chat_id)

    # db_add_chatusers(db, user.id, chat_id)
    # db_add_chatusers(db, chatInfo.friends, chat_id)

    # opened_chat_id = chat_id

    now_chatting_id.update({"chatid": result.chat_id})

    # print("chatid " + str(now_chatting_id.get("chatid")))
    # print("friends " + data.get("friends"))

    return


# 채팅방 리스트 불러오기
@app.get('/ChatListPage')
def get_chatListPage():

    return FileResponse("ChatList.html")


# 사용자가 참여하고 있는 채팅방 정보 불러오기
@app.get('/getChatList')
def get_chatList(db: Session = Depends(get_db),
                 user=Depends(manager)):

    return db_get_chattingList(db, user)


# 단톡 생성하는 페이지 불러오기
@app.get('/MakeGroupChatPage')
def get_MakeGroupChatPage():

    return FileResponse("MakeGroupChat.html")


# 현재 들어가려는 채팅방 정보를 서버 내 dictionary 안에 저장하는 함수
@app.post('/updateNowChatRoomStatus')
def update_chatStatus(chatInfo: ChatStatusUpdateSchema,
                      user=Depends(manager)):

    # chatInfo.chatid

    now_chatting_id.update({"chatid": chatInfo.chatid})

   # print("chatid " + str(now_chatting_id.get("chatid")))

    return


# 채팅방 페이지 받아오기
@app.get('/chatroom')
def get_chatroom():

    return FileResponse("ChatRoom.html")


# 현재 채팅방 사용자가 들어간 채팅방 아이디 받아오는 함수
@app.get('/getchatId')
def get_chatId():

    # print("현재 채팅방 Id " + str(now_chatting_id.get("chatid")))

    return now_chatting_id.get("chatid")


# 메세지들 받아오기
@app.post("/getmessages", response_model=List[MessageSchema])
def get_talks(item: MesesageGetSchema,
              db: Session = Depends(get_db)):

    return db_get_messages(db, item)


# 메세지 추가하기 (메세지를 추가하면 해당 채팅방의 lastmessage도 update)
@app.post("/addmessages", response_model=List[MessageSchema])
def post_addmessage(item: MessageRequestCreate,
                    db: Session = Depends(get_db),
                    user=Depends(manager)):

    messageContent = item.content
    chatid = item.chatid

    db_update_lastmessage(db, chatid, messageContent)

    return db_add_message(db, item, user)


# 프로필 페이지 돌려주는 함수
@app.get("/getProfilePage")
def get_profile():

    return FileResponse("profile.html")


# 프로필 수정하는 페이지 돌려주는 함수
@app.get("/updateProfilePage")
def get_updateProfilePage():

    return FileResponse("updateProfile.html")


# 프로필 보기 클릭한 유저 정보를 서버에 저장하는 로직을 진행하는 함수 (닥셔너리에 저장)
@app.post("/updateProfileUserDictionary")
def update_userStatus(item: profileUserRequestSchema,
                      db: Session = Depends(get_db)):

    res = db_get_user(db, item.userid)

    now_chatting_id.update({"userId": item.userid})

    # print("UserId : " + item.userid)

    return res


# 친구리스트 페이지에서 클릭된 사용자 정보를 받아오는 함수
@app.get("/getClickedUser")
def get_clickedUser(db: Session = Depends(get_db)):

    userid = now_chatting_id.get("userId")

    res = db_get_user(db, userid)

    return res


# 프로필 수정처리해주는 함수
@app.post("/updateProfile")
def update_userProfile(item: profileUpdateRequestSchema,
                       db: Session = Depends(get_db),
                       user=Depends(manager)):

    db_update_userProfile(db, item, user)

    return


# 채팅방에서 클릭된 이미지 파일 보여주는 페이지 로드 해주는 함수
@app.get("/showimage")
def get_showimage():

    return FileResponse("ShowImage.html")


# 채팅방에서 클릭한 사진의 url을 서버 딕셔너리에 저장하는 함수
@app.post("/setImageDictionary")
def set_image(item: imageUpdateSchema):

    now_chatting_id.update({"imageLink": item.imageLink})

    return "success!"


# 채팅방에서 클릭된 이미지 파일 url을 서버에서 받아오기
@app.get("/getimage")
def get_image():

    # print(now_chatting_id.get("imageLink"))

    return {"image": now_chatting_id.get("imageLink")}


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


connectionManager = ConnectionManager()


# WebSocket 서버 라우트
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connectionManager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await connectionManager.broadcast(f"{data}")
    except Exception as e:
        pass
    finally:
        await connectionManager.disconnect(websocket)


def run():
    import uvicorn
    uvicorn.run(app)


if __name__ == "__main__":
    run()
