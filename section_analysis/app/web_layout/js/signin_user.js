"use strict";

const username = document.getElementById("username");
const password = document.getElementById("password");
const button = document.getElementById("submit_button");
const response_text = document.getElementById("response_text");

button.addEventListener("click", function () {
    const user_data = new FormData();
    user_data.append("username", username.value);
    user_data.append("password", password.value);

    if (username.value == null || username.value == "") {
        alert("Please Fill All Required Field");
        return false;
    }

    if (password.value == null || password.value == "") {
        alert("Please Fill All Required Field");
        return false;
    }

    signin_user(user_data);
});


function signin_user(user_data) {
    const url = "/auth/token";
    const my_settings = {
        method: 'POST',
        body: user_data
    };
    fetch(url, my_settings)
        .then(function (response) {
            if (response.ok) {
                return response.text()
                    .then(function (text) {
                        localStorage.setItem("Authorization", "Bearer " + JSON.parse(text)["access_token"]);
                        const my_headers = new Headers();
                        my_headers.append("Authorization", "Bearer " + JSON.parse(text)["access_token"]);
                        const url = "/users/sign_in";
                        const my_settings = {
                            method: "GET",
                            headers: my_headers,
                        };
                        fetch(url, my_settings)
                            .then(function (response) {
                                return response.text();
                            })
                            .then(function (text) {
                                document.body.innerHTML = text;
                            });
                    });
            }
            else {
                return response.json()
                    .then(function (json) {
                        // throw Error(json["detail"]);
                        response_text.textContent = json["detail"];
                    });
            }
        });
};


function check(user_data) {
    for (elem in user_data) {
        if (user_data[elem] == null || user_data[elem] == "") {
            alert("Please Fill All Required Field");
            return false;
        }
    }
    return true;
}