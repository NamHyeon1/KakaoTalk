

$(document).ready(function () {
    $("#container").empty();
    fill_instruction();

    // 채팅 만들기 클릭 핸들러 등록
    $('#btnStartChat').click(function () {

        let users = document.getElementsByClassName('clicked_user');

        let you = ""

        // 클릭된 사용자들을 하나의 string으로 모음
        for (let i = 0; i < users.length; i++) {
            console.log(users[i].childNodes[0].innerText);

            you += users[i].childNodes[0].innerText + " "
        }

        let count = users.length;

        if (count == 1) {

            alert("1명 이상 선택해주세요!");
            return;

        }


        let data = {
            "friends": you,
            "number": count,
            "isGroup": 1,
            "chatid": -1
        }

        console.log(data);

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
})

// 사용자에게 방법 알려주는 부분 채우기
function fill_instruction() {

    let loginUser = "<p style='font-weight:bold;'>단톡에 추가할 사람 ID를 클릭해주세요<\p>";

    $("#container").append(loginUser);
    $("#container").append("<hr>");

    get_friend();
}

// 친구들 받아와서 이름 추가하기
function get_friend() {
    $.getJSON("/getFriendList", fill_users);
}

function fill_users(users) {
    users.forEach(user => {
        let userP = "<p onclick='clickHandler(this)' style='padding:5px;'><span class='userid' >" + user.friend + '</span><\p>'

        $("#container").append(userP);

    });



}

// click 했을때 클래스 토글
function clickHandler(user) {
    // console.log(user);
    user.classList.toggle('clicked_user');
}








