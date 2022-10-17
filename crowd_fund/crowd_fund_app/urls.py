from allauth.account import views
from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView, ResendEmailVerificationView
from django.urls import path, re_path, include
from crowd_fund_app.crowd_fund_app.views import user_edit, user_password_reset, user_password_reset_request, \
    DeleteUserView, user_delete, user_delete_direct, CustomPasswordResetConfirmView, CustomPasswordResetView

urlpatterns = [
    path('registration/account-confirm-email/<str:key>/',
         ConfirmEmailView.as_view()),
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('edit/', user_edit, name='user_edit'),
    path('delete/', DeleteUserView.as_view(), name='user_delete'),
    path('delete/confirm/<slug:uidb64>/<slug:token>/',
         user_delete, name='user_delete_confirm'),
    path('delete_direct/',
         user_delete_direct, name='user_delete_direct'),
    path('password/reset_request/', user_password_reset_request),
    path('password/reset/confirm/<slug:uidb64>/<slug:token>/',
         user_password_reset, name='password_reset_confirm'),
    path('password/reset/confirm2/<slug:uidb64>/<slug:token>/',
         CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm2'),
    # path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset_request'),
    path('', include('dj_rest_auth.urls')),
]

