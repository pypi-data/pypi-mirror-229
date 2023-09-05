from django.conf import settings
from django.urls import path
from .views.base import manifest
from .views.login import (
    Login,
    Logout,
    login_check,
)
from .views.password import (
    APIPasswordChange,
    APIPasswordResetView,
    APIPasswordResetConfirmView,
)

app_name = 'django_accounts_api'
urlpatterns = [
    path('', manifest, name='manifest'),

    path('check', login_check, name='login_check'),
    path('login', Login.as_view(), name='login'),
    path('logout', Logout.as_view(), name='logout'),

    path('password_change', APIPasswordChange.as_view(), name='password_change'),
    path('password_reset', APIPasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', APIPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
