from django.contrib import admin
from django.urls import path

from singlecell_ai_insights.api.agent.views import (
    RunAgentChatStreamView,
    RunAgentChatView,
)
from singlecell_ai_insights.api.auth import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    MeView,
)
from singlecell_ai_insights.api.health import health_check
from singlecell_ai_insights.api.runs import RunViewSet

run_list = RunViewSet.as_view({'get': 'list'})
run_detail = RunViewSet.as_view({'get': 'retrieve'})
run_multiqc_report = RunViewSet.as_view({'get': 'multiqc_report'})

urlpatterns = [
    path('admin/', admin.site.urls),
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
    path('api/auth/me/', MeView.as_view(), name='auth_me'),
    # API urls
    path('api/health/', health_check, name='health'),
    path('api/runs/', run_list, name='run-list'),
    path('api/runs/<int:pk>/', run_detail, name='run-detail'),
    path(
        'api/runs/<int:pk>/multiqc-report/',
        run_multiqc_report,
        name='run-multiqc-report',
    ),
    path(
        'api/runs/<int:pk>/chat/',
        RunAgentChatView.as_view(),
        name='run-chat',
    ),
    path(
        'api/runs/<int:pk>/chat/stream/',
        RunAgentChatStreamView.as_view(),
        name='run-chat-stream',
    ),
]
