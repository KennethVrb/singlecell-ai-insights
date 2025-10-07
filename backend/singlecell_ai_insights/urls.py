from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Browseable api urls
    path('api/browse-auth/', include('rest_framework.urls')),
    # Auth urls
    path(
        'api/auth/login/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),
    path(
        'api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'
    ),
    # API urls
    path('api/', include('singlecell_ai_insights.api.urls')),
]
