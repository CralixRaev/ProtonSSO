import os

from flask import Flask
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_saml2.idp import SPHandler
from flask_saml2.utils import certificate_from_file

from db.database import db
from db.models.user import UserQuery
from idp.idp import ProtonIdentityProvider, IDP_CERTIFICATE, IDP_PRIVATE_KEY
from login_blueprint.login import login
from db.__all_models import *
from flask_login import LoginManager

from manage_blueprint.manage import manage

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_STRING") or \
                                        'sqlite:///test.db?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SMARTCAPTCHA_SERVER_KEY'] = os.getenv("SMARTCAPTCHA_SERVER_KEY")
app.config['SMARTCAPTCHA_CLIENT_KEY'] = os.getenv("SMARTCAPTCHA_CLIENT_KEY")

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login.index"
login_manager.login_message = "Пожалуйста, войдите, что бы просматривать эту страницу"
login_manager.login_message_category = "warning"
login_manager.session_protection = "strong"

app.config['SAML2_IDP'] = {
    'autosubmit': True,
    'certificate': IDP_CERTIFICATE,
    'private_key': IDP_PRIVATE_KEY,
}

SP_CERTIFICATE = certificate_from_file("../../PycharmProjects/protonCoin/sp_certificate.pem")

app.config['SAML2_SERVICE_PROVIDERS'] = [
    {
        'CLASS': 'idp.idp.AttributeSPHandler',
        'OPTIONS': {
            'display_name': 'Example Service Provider',
            'entity_id': 'http://localhost/saml/metadata.xml',
            'acs_url': 'http://localhost/saml/acs/',
            'certificate': SP_CERTIFICATE,
        },
    }
]

db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True, compare_type=True)

# app.add_url_rule('/login/', view_func=Login.as_view('login'))

idp = ProtonIdentityProvider()
app.register_blueprint(login, url_prefix="/login/")
app.register_blueprint(manage, url_prefix="/manage/")
app.register_blueprint(idp.create_blueprint(), url_prefix='/saml/')


@login_manager.user_loader
def load_user(user_id):
    return UserQuery.get_user_by_id(user_id)


def main():
    # with app.app_context():
    #     # ensure what default "bank" balance is present
    #     # BalanceQuery.ensure_bank_balance()
    app.run(debug=True, host='0.0.0.0', port=9000)


if __name__ == "__main__":
    main()
