//ログインと登録の遷移
let $id = (id) => document.getElementById(id);
var [login, register, form] = ['login', 'register', 'form'].map(id => $id(id));

[login, register].map(element => {
    element.onclick = function () {
        [login, register].map($ele => {
            $ele.classList.remove("active");
        });
        this.classList.add("active");
        this.getAttribute("id") === "register"?  form.classList.add("active") : form.classList.remove("active");
    }
});

//パスワード入力時の表示の有無
document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('register-password');
    const icon = document.getElementById('password-toggle');

    icon.addEventListener('click', function () {
        togglePasswordVisibility(passwordInput, icon);
    });
});

function togglePasswordVisibility(passwordInput, icon) {
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.textContent = '・';
    } else {
        passwordInput.type = 'password';
        icon.textContent = '&#x1F441;';
    }
}
