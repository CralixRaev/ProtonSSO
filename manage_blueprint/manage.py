import flask
import requests
from flask import Blueprint, render_template, redirect, request, session, current_app
from flask_login import login_user, current_user, login_required

from db.models.user import UserQuery
from login_blueprint.forms.login import LoginForm
from manage_blueprint.forms.avatar import AvatarForm
from manage_blueprint.forms.main import UserForm
from manage_blueprint.forms.password import PasswordForm
from utils import is_safe_url

manage = Blueprint('manage', __name__,
                  template_folder='templates',
                  static_folder='static')


@manage.route('/', methods=["GET", "POST"])
@login_required
def index():
    form_avatar = AvatarForm()
    form_main = UserForm()
    form_password = PasswordForm()
    context = {
        'title': "Ваш аккаунт",
        'form_avatar': form_avatar,
        'form_main': form_main,
        'form_password': form_password
    }
    return render_template("manage/account_info.html", **context)