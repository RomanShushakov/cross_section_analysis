"use strict";

const guest_full_name = "Guest";
const guest_email = "guest@guest.com";
const guest_username = "Guest";
const guest_password = "Guest";

const guest_data_signup = {
    "full_name": guest_full_name,
    "email": guest_email,
    "username": guest_username,
    "password": guest_password
}

const guest_data_signin = new FormData();
guest_data_signin.append("username", guest_username);
guest_data_signin.append("password", guest_password);

const current_user = document.getElementById("current_user");

window.onload = function () {
    const token = localStorage.getItem("Authorization");
    if (!token || token == "Bearer undefined") {
        signup_and_signin_guest(guest_data_signup);
        current_user.textContent = guest_username;
    }
    else {
        get_current_username(current_user);
    }
};


function signup_and_signin_guest(guest_data_signup) {
    const signup_url = "/auth/create_user";
    const my_signup_settings = {
        method: 'POST',
        body: JSON.stringify(guest_data_signup)
    };
    fetch(signup_url, my_signup_settings);

    const signin_url = "/auth/token";
    const my_signin_settings = {
        method: 'POST',
        body: guest_data_signin
    };
    fetch(signin_url, my_signin_settings)
        .then(function (response) {
            response.text()
                .then(function (text) {
                    localStorage.setItem("Authorization", "Bearer " + JSON.parse(text)["access_token"]);
                });
        });
};


function get_current_username(current_user) {
    const my_headers = new Headers();
    my_headers.append("Authorization", localStorage.getItem("Authorization"));
    const url = "/users/current_username";
    const my_settings = {
        method: "GET",
        headers: my_headers,
    };
    fetch(url, my_settings)
        .then(function (response) {
            if (response.ok) {
                response.text()
                    .then(function (text) {
                        current_user.textContent = JSON.parse(text)["username"];
                    });
            }
            else {
                response.json()
                    .then(function (json) {
                        // throw Error(json["detail"]);
                        alert("Your session was expired, please sign in again");
                        signup_and_signin_guest(guest_data_signup);
                        current_user.textContent = guest_username;
                    });
            }
        });
}
