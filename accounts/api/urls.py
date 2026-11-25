from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import RegisterView, ActivationView, LoginView, LogoutView, CustomTokenRefreshView, PasswordResetView, PasswordConfirmView



urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('activate/<uidb64>/<token>/', ActivationView.as_view(), name="activation-mail"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("password_reset/", PasswordResetView.as_view(), name="reset-password"),
    path("password_confirm/<uidb64>/<token>/", PasswordConfirmView.as_view(), name="confirm-password")
]