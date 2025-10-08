from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .serializers import (
    CookieTokenObtainPairSerializer,
    CookieTokenRefreshSerializer,
)


def _cookie_kwargs(path):
    kwargs = {
        'httponly': settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        'secure': settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        'samesite': settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        'path': path,
    }
    domain = settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN']
    if domain:
        kwargs['domain'] = domain
    return kwargs


def _delete_cookie(response, name, path):
    domain = settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN']
    if domain:
        response.delete_cookie(name, path=path, domain=domain)
    else:
        response.delete_cookie(name, path=path)


class CookieMixin:
    def set_token_cookies(self, response, access, refresh):
        if access:
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE'],
                access,
                max_age=int(
                    settings.SIMPLE_JWT[
                        'ACCESS_TOKEN_LIFETIME'
                    ].total_seconds()
                ),
                **_cookie_kwargs(settings.SIMPLE_JWT['AUTH_COOKIE_PATH']),
            )
        if refresh:
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE'],
                refresh,
                max_age=int(
                    settings.SIMPLE_JWT[
                        'REFRESH_TOKEN_LIFETIME'
                    ].total_seconds()
                ),
                **_cookie_kwargs(
                    settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE_PATH']
                ),
            )

    def clear_token_cookies(self, response):
        _delete_cookie(
            response,
            settings.SIMPLE_JWT['AUTH_COOKIE'],
            settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        _delete_cookie(
            response,
            settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE'],
            settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE_PATH'],
        )


class CookieTokenObtainPairView(CookieMixin, TokenObtainPairView):
    serializer_class = CookieTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data.copy()
        self.set_token_cookies(
            response, data.get('access'), data.get('refresh')
        )
        response.data = {'user': data.get('user')}
        return response


class CookieTokenRefreshView(CookieMixin, TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def get_serializer(self, *args, **kwargs):
        data = kwargs.get('data')
        if data is not None and 'refresh' not in data:
            refresh_cookie = self.request.COOKIES.get(
                settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE']
            )
            if refresh_cookie:
                data = data.copy()
                data['refresh'] = refresh_cookie
                kwargs['data'] = data
        return super().get_serializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data.copy()
        self.set_token_cookies(
            response, data.get('access'), data.get('refresh')
        )
        response.data = {'detail': 'refreshed'}
        return response


class LogoutView(CookieMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_cookie = request.COOKIES.get(
            settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE']
        )
        if refresh_cookie:
            try:
                RefreshToken(refresh_cookie).blacklist()
            except Exception:
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        self.clear_token_cookies(response)
        return response
