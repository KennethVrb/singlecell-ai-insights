from django.contrib import admin
from django.urls import include, path

from singlecell_ai_insights.api.auth import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
)
from singlecell_ai_insights.api.health import health_check
from singlecell_ai_insights.api.runs import RunListView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Browseable api urls
    path('api/browse-auth/', include('rest_framework.urls')),
    # Auth urls
    path(
        'api/auth/login/',
        CookieTokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),
    path(
        'api/auth/refresh/',
        CookieTokenRefreshView.as_view(),
        name='token_refresh',
    ),
    path('api/auth/logout/', LogoutView.as_view(), name='token_logout'),
    # API urls
    path('api/health/', health_check, name='health'),
    path('api/runs/', RunListView.as_view(), name='run-list'),
]
