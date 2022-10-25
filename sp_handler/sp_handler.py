import flask_saml2
import urllib.parse
from flask_saml2.sp import ServiceProvider


class ProtonServiceProvider(ServiceProvider):
    SAML_BASE_URL = "https://sso.protonmos.ru/saml/"

    def __init__(self, identity_providers, cert, private_key, **kwargs):
        super().__init__(**kwargs)
        self._cert = cert
        self._private_key = private_key
        self.identity_providers = identity_providers

    def get_sp_config(self):
        return {
            'certificate': self._cert,
            'private_key': self._private_key,
        }

    def get_identity_providers(self):
        return [{
            "CLASS": "flask_saml2.sp.idphandler.IdPHandler",
            'OPTIONS': {
                'display_name': 'ПРОтоКоин SSO',
                'entity_id': urllib.parse.urljoin(self.SAML_BASE_URL, "metadata.xml"),
                'sso_url': urllib.parse.urljoin(self.SAML_BASE_URL, "login"),
                'slo_url': urllib.parse.urljoin(self.SAML_BASE_URL, "logout"),
                'certificate': self._cert,
            },
        }]

