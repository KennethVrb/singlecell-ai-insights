from django.conf import settings
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)


class CookieTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'username': self.user.username,
            'email': self.user.email,
        }
        return data


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = attrs.get('refresh')
        if not refresh:
            request = self.context.get('request')
            if request is not None:
                refresh = request.COOKIES.get(
                    settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE']
                )
                if refresh:
                    attrs['refresh'] = refresh
        return super().validate(attrs)
