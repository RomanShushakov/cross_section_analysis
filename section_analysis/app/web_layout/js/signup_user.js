"use strict";

const fullname = document.getElementById("full_name");
const email = document.getElementById("email");
const username = document.getElementById("username");
const password = document.getElementById("password");
const button = document.getElementById("register_button");

const signin_button = "<button><a href='/web_layout/sign_in.html' type='submit'>sign in</a></button>"

const response_text = document.getElementById("response_text");

button.addEventListener('click', function () {
    const user_data = {
        "full_name": full_name.value,
        "email": email.value,
        "username": username.value,
        "password": password.value
    }

    if (!check(user_data)) {
        return false;
    }
    else {
        register_user(user_data);

        fullname.value = "";
        email.value = "";
        username.value = "";
        password.value = "";
    }
});

function register_user(user_data) {
    const url = "/auth/create_user";
    const my_settings = {
        method: 'POST',
        body: JSON.stringify(user_data)
    };
    fetch(url, my_settings)
        .then(function (response) {
            if (response.ok) {
                return response.text()
                    .then(function (text) {
                        document.getElementById("registration_form").innerHTML = "";
                        response_text.textContent = text;
                        document.getElementById("signin_button_location").innerHTML = signin_button;
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
    /* .catch(function(err) {
      console.log(err);
      response_text.textContent = err;
    }); */
};

function check_email(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function check(user_data) {
    let elem = null;
    for (elem in user_data) {
        if (user_data[elem] == null || user_data[elem] == "") {
            alert("Please Fill All Required Field");
            return false;
        }
    }
    if (!check_email(user_data.email)) {
        alert("You have entered an invalid email address");
        return false;
    }
    return true;
}