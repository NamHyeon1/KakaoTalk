let ws = new WebSocket("ws://localhost:8000/ws");

// message send button 담고있음
let wsSend;


$(document).ready(function () {
    getChatId();
    get_loginedUser();

    wsSend = $('#u1sendBtn');

    // 메세지 보내기 버튼 클릭 핸들러 등록
    $('#u1sendBtn').click(function () {

        sendMessage();
    });

    // 이미지 보내기 버튼 클릭 핸들러 등록
    $('#btnImageSend').click(function () {
        sendImage();
    })

    $(function () {
        $('textarea').on('keydown', function (event) {
            if (event.keyCode == 13) {
                if (!event.shiftKey) {
                    event.preventDefault();

                    let parent = $(this).parent();
                    let button = parent.find("button");
                    button.click();
                }
            }

        });
    });
})

// 웹소켓 받았을 때 처리
function webSocketSend(event) {
    let userid = $('#userId').text();
    ws.send(userid);
    event.preventDefault();
}

// 로그인한 사용자 정보 페이지에 저장하기
function get_loginedUser() {
    $.getJSON("/getLoginUser", loginedUser)
}
function loginedUser(user) {

    let userid = user[0].id

    $("#userId").text(userid);

}

// 서버에서 채팅방 아이디 받아오기
function getChatId() {
    $.getJSON('/getchatId', function (chatId) {
        // console.log("현재 채팅방 id :" + chatId);

        document.getElementById("chatid").innerText = chatId

        get_messages();
        // console.log($('#chatid').text())
    })


}

// 페이지가 로드 됐을 때 chatting방 id 정보를 활용하여 메세지를 받고 보여주는 함수
function get_messages() {

    let chatId = $('#chatid').text();

    data = {
        "chatid": chatId
    }

    console.log(data)

    $.ajax({
        url: "/getmessages",
        type: "post",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function (result) {
            show_messages(result);

        }
    })
}

// 메세지 보내기 사용자 아이디와 내용, 톡방 아이디, 
function sendMessage() {
    let userid = $('#userId').text();
    let inputText = $('#u1text').val();
    let chatId = $('#chatid').text();
    let time;

    $('#u1text').val('');


    // if (userid.length == 0) {
    //     // console.log("ID 입력안함!")
    //     alert("ID 입력하세요!")
    //     return;
    // }

    let tmp = inputText.trim();

    inputText.replaceAll("\n", "<br/>");

    // 빈 채팅 안 보내지게 구현
    if (tmp.length == 0) {
        console.log("empty string!");
        return;
    }

    // 시간 받아오기 js 시간 형식을 카톡 시간 형식으로 바꿔주는 함수
    time = getTime();

    let data = {
        "userid": userid,
        "content": inputText,
        "time": time,
        "chatid": chatId,
        "isImg": 0
    }

    console.log(data);

    $.ajax({
        url: "/addmessages",
        type: "post",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function (result) {
            show_messages(result);
            webSocketSend(wsSend);
        }
    })

    // ws.send(userId + ": " + input.value);

}

// 이미지 보내기
function sendImage() {
    let userid = $('#userId').text();
    let temp = $('#SendingImage').val();
    let chatId = $('#chatid').text();
    let time;

    console.log(temp)


    let image = temp.split("\\")[2]
    let imageLink = ""
    if (image == undefined) {
        alert("이미지를 선택해주세요!")
        return;
    }
    imageLink = "static/" + image


    $('#SendingImage').val('');

    time = getTime();

    let data = {
        "userid": userid,
        "content": imageLink,
        "time": time,
        "chatid": chatId,
        "isImg": 1
    }

    console.log(data);


    $.ajax({
        url: "/addmessages",
        type: "post",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function (result) {
            show_messages(result);
            webSocketSend(wsSend);
        }
    })


}

// 현재 시간 추출하기
function getTime() {
    let date = new Date();

    let hour = date.getHours();
    let minute = date.getMinutes();

    let ampm = (hour > 12) ? "오후" : "오전";

    hour = hour % 12;

    if (hour == 0) {
        hour = '12';
    }

    if (hour < 10) {
        hour = '0' + hour;
    }

    if (minute < 10) {
        minute = '0' + minute;
    }

    time = ampm + " " + hour + ":" + minute;

    return time;
}

// 메세지 보여주기
function show_messages(messages) {

    $('#u1Content').empty();

    let userid = $('#userId').text();

    messages.forEach(item => {

        if (item.isImg == 1) {

            loadImage(item)

        } else {

            let mtexts = '<div class="mtexts">' + '<div class="mtime">' + item.time + '</div> ' + '<div class="mine speech_bubble"><pre>' + item.content + '</pre></div>' + '</div>';
            let ytexts = '<div class=""><div class="name">' + item.userid + '</div><div class="ytexts">' + '<div class="yours speech_bubble"><pre>' + item.content + '</pre></div> ' + '<div class="ytime">' + item.time + '</div>' + '</div>';

            if (userid == item.userid) {
                $('#u1Content').append(mtexts);
            } else {
                $('#u1Content').append(ytexts);
            }
        }

        $('#u1Content').scrollTop($('#u1Content')[0].scrollHeight);

    });

}

// 메세지가 이미지일 때 처리하는 함수
function loadImage(item) {

    let userid = $('#userId').text();


    let mtexts = '<div class="mtexts">' + '<div class="mtime posup">' + item.time + '</div> ' + '<img onclick="messageClickHandler(this)" src="' + item.content + '" width="150">' + '</div>';
    let ytexts = '<div class=""><div class="name">' + item.userid + '</div><div class="ytexts">' + '<img onclick="messageClickHandler(this)" src="' + item.content + '" width="150">' + '<div class="ytime">' + item.time + '</div>' + '</div>';


    if (userid == item.userid) {
        $('#u1Content').append(mtexts);
    } else {
        $('#u1Content').append(ytexts);
    }
}

// 이미지 클릭했을 때 새창에서 볼 수 있도록 구현한 함수
function messageClickHandler(img) {

    imageLink = img.src

    console.log(imageLink)

    data = {
        "imageLink": imageLink
    }

    $.ajax({
        url: "/setImageDictionary",
        type: "post",
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function (result) {
            console.log(result)

            window.open("/showimage", "_blank");

            // window.location = '/showimage'
        }
    })
}



// 실시간 채팅 구현 (웹소켓)
ws.onmessage = function (event) {
    let content = event.data;

    let userid = $("#userId").text();

    if (content != userid) {
        // console.log("지금 사용자 : " + userid);
        // console.log("카톡 보낸사람 : " + content);

        get_messages();
    }

}

