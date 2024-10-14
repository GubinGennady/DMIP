from django.urls import path

from app.apps import AppConfig

from app.views import IndexView, RegView, AuthView, Add

app_name = AppConfig.name

urlpatterns = [
    path('list', IndexView.as_view(), name='list'),
    path('', RegView.as_view(), name='reg'),
    path('auth', AuthView.as_view(), name='auth'),
    path('add', Add.as_view(), name='add')
]
