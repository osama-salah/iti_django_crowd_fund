from allauth.account import views
from allauth.account.views import ConfirmEmailView
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView, ResendEmailVerificationView
from dj_rest_auth.views import UserDetailsView
from django.urls import path, re_path, include, reverse
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from crowd_fund_app.crowd_fund_app.views import user_edit, user_password_reset, user_password_reset_request, \
    DeleteUserView, user_delete, user_delete_direct, CustomPasswordResetConfirmView, CustomPasswordResetView, \
    UserProjectsViewSet, user_details, CustomLoginView, resend_email_post, CustomUserDetailsView, \
    user_logout

urlpatterns = [
    # path('registration/account-confirm-email/<str:key>/',
    #      ConfirmEmailView.as_view()),
    re_path(r'^registration/account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(),
            name='account_confirm_email'),
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('email_confrmed/', TemplateView.as_view(template_name='crowd_fund_app/account_confirm_email.html'),
         name='email_confirmed'),
    path('edit/', user_edit, name='user_edit'),
    path('delete/', DeleteUserView.as_view(), name='user_delete'),
    path('delete/confirm/<slug:uidb64>/<slug:token>/',
         user_delete, name='user_delete_confirm'),
    path('delete_direct/',
         user_delete_direct, name='user_delete_direct'),
    path('password/reset_request/', user_password_reset_request, name='user_password_reset_request'),
    path('password/reset/confirm/<slug:uidb64>/<slug:token>/',
         user_password_reset, name='password_reset_confirm'),
    path('password/reset/confirm2/<slug:uidb64>/<slug:token>/',
         CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm2'),
    path('password/reset/', CustomPasswordResetView.as_view(), name='password_reset_request'),
    path('home/', user_details, name='user_details'),
    path('login/', CustomLoginView.as_view(), name='rest_login'),
    path('user-logout/', user_logout, name='user_logout'),
    # path('logout/', CustomLogoutView.as_view(), name='rest_logout'),
    path('resend_email_post/<email>/', resend_email_post, name='resend_email_post'),
    # path('', get_user_details),
    # path('', UserDetailsView.as_view(), name='rest_user_details'),
    path('profile/', CustomUserDetailsView.as_view(), name='user_profile'),
    path('', include('dj_rest_auth.urls')),
    # This path has already been included from 'dj_rest_auth.urls'. However, it is re-included just to
    # match user/ path
]

router = SimpleRouter()
router.register('projects', UserProjectsViewSet, basename="user_projects"),
# router.register('home', UserViewSet.list(), basename="user_details")
urlpatterns.extend(router.urls)
