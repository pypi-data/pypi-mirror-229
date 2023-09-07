"Provide a RemoteUserAuthentication class for Django Rest Framework"
from rest_framework import authentication


class DLSRemoteUserAuthentication(authentication.RemoteUserAuthentication):
    "Authentication for Django Rest Framework inside a Sandstorm grain"
    header = "HTTP_X_SANDSTORM_USER_ID"
