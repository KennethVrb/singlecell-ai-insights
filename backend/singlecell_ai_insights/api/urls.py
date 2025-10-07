from django.urls import path

from . import views
from .runs import RunListView

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('runs/', RunListView.as_view(), name='run-list'),
]
