#!/usr/bin/env python3
import logging

import attr
from flask import abort, redirect, request, session, url_for, render_template, Blueprint
from flask.views import MethodView
from flask_login import current_user, logout_user

from flask_saml2.idp import IdentityProvider, SPHandler
from flask_saml2.utils import private_key_from_file, certificate_from_file

# from tests.idp.base import CERTIFICATE, PRIVATE_KEY, User
# from tests.sp.base import CERTIFICATE as SP_CERTIFICATE


IDP_CERTIFICATE = certificate_from_file("./idp/certificate.pem")
IDP_PRIVATE_KEY = private_key_from_file("./idp/private-key.pem")

logger = logging.getLogger(__name__)


@attr.s
class User:
    username = attr.ib()
    email = attr.ib()


class ProtonIdentityProvider(IdentityProvider):
    def login_required(self):
        if not self.is_user_logged_in():
            next = url_for('login.index', next=request.url)

            abort(redirect(next))

    def is_user_logged_in(self):
        return current_user.is_authenticated

    def logout(self):
        logout_user()

    def get_current_user(self):
        return current_user

    def get_user_nameid(self, user, attribute):
        if attribute == 'urn:oasis:names:tc:SAML:2.0:nameid-format:email':
            return self.get_user_email(user) or user.login

        raise NotImplementedError("Can't fetch attribute {} from user".format(attribute))


#
# class Login(MethodView):
#     def get(self):
#         # options = ''.join(f'<option value="{user.username}">{user.email}</option>'
#         #                   for user in users.values())
#         # select = f'<div><label>Select a user: <select name="user">{options}</select></label></div>'
#
#         # next_url = request.args.get('next')
#         # next = f'<input type="hidden" name="next" value="{next_url}">'
#         #
#         # submit = '<div><input type="submit" value="Login"></div>'
#         #
#         # form = f'<form action="." method="post">{select}{next}{submit}</form>'
#         # header = '<title>Login</title><p>Please log in to continue.</p>'
#         #
#         # return header + form
#         return render_template("templates/idp/base.html")
#
#     def post(self):
#         user = request.form['user']
#         next = request.form['next']
#
#         session['user'] = user
#         logging.info("Logged user", user, "in")
#         logging.info("Redirecting to", next)
#
#         return redirect(next)


class AttributeSPHandler(SPHandler):
    def build_assertion(self, request, *args, **kwargs):
        print(current_user.group_id)
        return {
            **super().build_assertion(request, *args, **kwargs),
            'ATTRIBUTES': {
                'id': str(current_user.id),
                'login': current_user.login,
                'email': current_user.email,
                'name': current_user.name,
                'surname': current_user.surname,
                'patronymic': current_user.patronymic,
                'is_admin': str(current_user.is_admin),
                'is_teacher': str(current_user.is_teacher),
                'group.id': str(current_user.group_id),
                'group.stage': str(current_user.group.stage),
                'group.letter': current_user.group.letter,
                'avatar': current_user.avatar,
            },
        }
