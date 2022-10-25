import flask
import requests
from flask import Blueprint, render_template, redirect, request, session, current_app
from flask_login import login_user

from db.models.user import UserQuery
from login_blueprint.forms.login import LoginForm
from utils import is_safe_url

login = Blueprint('login', __name__,
                  template_folder='templates',
                  static_folder='static')


def _check_captcha(token):
    answer = requests.get(
        "https://captcha-api.yandex.ru/validate",
        {
            "secret": current_app.config['SMARTCAPTCHA_SERVER_KEY'],
            "token": token,
            "ip": request.remote_addr
        },
        timeout=1
    )
    server_output = answer.json()
    if answer.status_code != 200:
        current_app.logger.error(
            f"Allowing access due to captcha error: code={answer.status_code}; message={server_output()}")
        return True
    print(server_output)
    return server_output['status'] == 'ok'


@login.route('/', methods=["GET", "POST"])
def index():
    form = LoginForm()
    context = {
        'form': form,
        'title': 'Авторизация'
    }
    if form.validate_on_submit():
        if not _check_captcha(request.form.get("smart-token")):
            flask.flash("Вы не прошли капчу", "danger")
        else:
            user = UserQuery.get_user_by_login(form.login.data)
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_path = request.args.get("next")
                if not is_safe_url(next_path):
                    return flask.abort(400)
                return redirect(next_path)
            else:
                flask.flash("Неправильный логин или пароль", "danger")
    return render_template("login/login.html", **context)
