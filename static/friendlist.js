$(document).ready(function () {
    $("#container").empty();
    get_loginedUser();

})

// 현재 로그인한 사용자를 추가
function get_loginedUser() {
    $.getJSON("/getLoginUser", fill_loginedUser)
}

// p element를 만들어서 append
function fill_loginedUser(user) {

    let id = user[0].id


    let loginUser = "<p><span class='userid'>" + id + '</span><span style="float: right"><button class="showprofile">프로필 보기</button></span><p>'

    $("#container").append(loginUser);
    $("#container").append("<hr>");

    get_friend();
}


// 친구리스트를 받아서 page에 append하기
function get_friend() {
    $.getJSON("/getFriendList", fill_users);
}


function fill_users(users) {
    users.forEach(user => {

        let userP = "<p><span class='userid'>" + user.friend + '</span><span style="float: right"><button class="showprofile">프로필 보기</button> <button class="startchat">채팅</button></span><p>'

        $("#container").append(userP);

    });


    // 채팅시작하기 클릭했을 때 채팅방 정보를 서버에 저장하도록 click listener 등록
    $('.startchat').click(function () {

        let you = $(this).parent().parent().find('span.userid').text();

        console.log(you);

        let data = {
            "friends": you,
            "number": 2,
            "isGroup": 0,
            "chatid": -1
        }

        // 서버 내 딕셔너리에 현재 들어가고자 하는 채팅방 아이디 정보 저장
        $.ajax({
            url: "/createChatRoom",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (data, txtStatus, xhr) {

                window.location = '/chatroom';

            },
            error: function (event) {
                console.log("실패..");
            }
        })


    })

    // 프로필보기 클릭했을 때 보여주도록 click listener 등록
    $('.showprofile').click(function () {


        // 백엔드 내에 프로필 보기 클릭한 사용자 정보 저장하는 딕셔너리 업데이트 (profile 사이트 로드할 때 해당 유저 정보를 로드하기 위하여 필요해서)

        let userid = $(this).parent().parent().find('span.userid').text();

        console.log(userid)

        let data = {
            "userid": userid,
        }

        $.ajax({
            url: "/updateProfileUserDictionary",
            type: "post",
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function (data, txtStatus, xhr) {


                window.location = '/getProfilePage';

            },
            error: function (event) {
                console.log("실패..");
            }
        })

        // window.location = '/getProfilePage'
    })
}