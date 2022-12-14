import http
import os

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress, EmailConfirmation, EmailConfirmationHMAC
from allauth.account.utils import url_str_to_user_pk, user_pk_to_url_str, user_username
from allauth.account.views import ConfirmEmailView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.utils import build_absolute_uri
from dj_rest_auth.app_settings import JWTSerializer, TokenSerializer
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.core import signing
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.registration.views import SocialLoginView, RegisterView, SocialConnectView
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView, LoginView, UserDetailsView
from django.conf import settings
from django.contrib.auth import user_logged_out, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework import status, exceptions
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from crowd_fund_app.forms import UserEditForm, UserRegisterForm
from crowd_fund_app.models import CustomUser
from crowd_fund_app.serializers import CustomUserDeleteSerializer
# This view sends a message to current user's registered email
from projects.models import Project, Donation
from projects.projects.views import ProjectViewSet


def user_details(request):
    user = CustomUser.objects.get(id=request.user.id)
    projects = Project.objects.filter(user_id=request.user.id)
    donations = Donation.objects.filter(user_id=request.user.id)
    return render(request, 'crowd_fund_app/user_details.html',
                  context={
                      'user': user,
                      'projects': projects,
                      'donations': donations})


def resend_email_form(request):
    email = request.POST.get('email', None)
    return resend_email_post(request, email)


def resend_email_post(request, email):
    email = EmailAddress.objects.filter(email=email).first()
    if not email:
        return render(request, 'crowd_fund_app/register_msg.html', {'messages': ["This email doesn't exist"]})
    if email.verified:
        return render(request, 'crowd_fund_app/register_msg.html',
                      {'messages': ["This email has already been verified"]})
    email.send_confirmation(request)
    return render(request, 'crowd_fund_app/register_msg.html', {'messages': [f'Activation email was sent to {email}']})


def user_register(request):
    form = UserRegisterForm()
    return render(request, 'crowd_fund_app/signup.html', {'form': form})


class CustomRegisterView(RegisterView):

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, args, kwargs)
        except ValidationError as ex:
            msg = ["Please, correct the following errors:"]
            for er in ex.detail.values():
                msg.append(er[0].title())
            return render(request, 'crowd_fund_app/register_msg.html', {'messages': msg}, status=HTTP_400_BAD_REQUEST)
        return render(request, 'crowd_fund_app/register_msg.html', {'message': 'Verification e-mail sent.'})


class CustomLoginView(LoginView):

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)

        try:
            self.serializer.is_valid(raise_exception=True)
        except ValidationError as v:
            if 'E-mail is not verified.' in str(v.detail):
                return render(request, 'crowd_fund_app/email_unverified.html',
                              context={'email': self.request.data['email']}, status=HTTP_400_BAD_REQUEST)
            return render(request, 'crowd_fund_app/login_error.html', {'message': v}, status=HTTP_400_BAD_REQUEST)

        self.login()
        return redirect(reverse('home'))


def user_logout(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist):
        pass

    if getattr(settings, 'REST_SESSION_LOGIN', True):
        user = getattr(request, "user", None)
        if not getattr(user, "is_authenticated", True):
            user = None
        user_logged_out.send(sender=user.__class__, request=request, user=user)
        request.session.flush()
        if hasattr(request, "user"):
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
    response = render(request, 'crowd_fund_app/logout_successful.html', status=status.HTTP_200_OK)

    if getattr(settings, 'REST_USE_JWT', False):
        from dj_rest_auth.jwt_auth import unset_jwt_cookies
        unset_jwt_cookies(response)
    return response


# class CustomLogoutView(LogoutView):
#     def logout(self, request):
#         response = super().logout(request)
#         if response.status_code == status.HTTP_200_OK:
#             return HttpResponse(r'You have successfully logged out.')
#             # r'<meta http-equiv = "refresh" content = "3; url = http://localhost:8000" />')
#         return HttpResponse(r'Problem logging out.'
#                             r'<meta http-equiv = "refresh" content = "3; url = http://localhost:8000" />')


# def get_user_details(request):
#     return redirect(reverse('rest_user_details'), pk=request.user.id)


def get_user_public_profile(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if user:
        print('user: ', user)
        return render(request, 'crowd_fund_app/user_public_profile.html', context={'user': user})
    return render(request, 'crowd_fund_app/register_msg.html',
                  {'messages': ["This user doesn't exist"]}, status=HTTP_400_BAD_REQUEST)


class CustomUserDetailsView(UserDetailsView):
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        form = UserEditForm(instance=user)
        return render(request, 'crowd_fund_app/user_profile.html', context={'form': form, 'user': user})


def user_delete_direct(request):
    if request.method == 'GET':
        return render(request, 'crowd_fund_app/user_delete_form.html')

    email = request.user.email
    password = request.POST.get('password', None)

    # This part is derived from dj-rest-auth.serializers.LoginSerializer. (_validate_email and authenticate)
    if email and password:
        try:
            user = authenticate(request, email=email, password=password)
        except PermissionDenied:
            return render(request, 'crowd_fund_app/register_msg.html',
                          {'messages': ['Wrong credentials']})
    else:
        return render(request, 'crowd_fund_app/register_msg.html',
                      {'messages': ['Must include "email" and "password".']}, status=HTTP_400_BAD_REQUEST)

    # This part of code is taken from dj-rest-auth.serializers.PasswordResetSerializer.save and
    # dj-rest-auth.forms.AllAuthPasswordResetForm.save
    if user is None:
        return render(request, 'crowd_fund_app/register_msg.html',
                      {'messages': ['Wrong credentials provided']}, status=HTTP_400_BAD_REQUEST)

    current_site = get_current_site(request)
    # user = request.user
    # email = user.email
    token_generator = default_token_generator

    temp_key = token_generator.make_token(user)

    path = reverse(
        'user_delete_confirm',
        args=[user_pk_to_url_str(user), temp_key],
    )

    if getattr(settings, 'REST_AUTH_PW_RESET_USE_SITES_DOMAIN', False) is True:
        url = build_absolute_uri(None, path)
    else:
        url = build_absolute_uri(request, path)

    context = {
        'current_site': current_site,
        'user': user,
        'password_reset_url': url,
        'request': request,
    }
    if app_settings.AUTHENTICATION_METHOD != app_settings.AuthenticationMethod.EMAIL:
        context['username'] = user_username(user)
    get_adapter(request).send_mail('account/email/user_delete_key', email, context)
    return render(request, 'crowd_fund_app/user_account_delete_msg.html',
                  {'msg': 'A delete confirmation message was sent to your email. Please, follow the '
                          'instructions to complete.'})


# This view shows an email field to send the message to
def user_delete(request, uidb64, token):
    uid = url_str_to_user_pk(uidb64)
    try:
        user = CustomUser.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
            raise ValidationError({'token': ['Invalid value']})
        username = user.username
        os.remove(os.path.join(os.getcwd(), settings.MEDIA_URL[1:], str(user.picture)))
        user.delete()
        return render(request, 'crowd_fund_app/user_deleted.html', context={'username': username})
    except ValidationError:
        return HttpResponse('Expired or invalid token')
    except ValueError:
        pass
    except Exception as ex:
        return render(request, 'crowd_fund_app/user_account_delete_msg.html', {'msg': ex})
    return render(request, 'crowd_fund_app/user_account_delete_msg.html', {'msg': 'Unknown error occurred'})


def user_edit(request):
    user = request.user
    if request.method == 'POST':
        original_picture_path = str(user.picture)
        original_picture = os.path.basename(original_picture_path)
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            new_picture = request.FILES.get('picture')
            if new_picture is not None and new_picture != original_picture:
                try:
                    picture_full_path = os.path.join(os.getcwd(), settings.MEDIA_URL[1:], original_picture_path)
                    os.remove(picture_full_path)
                except FileNotFoundError:
                    pass
            user = form.save()
            return redirect(reverse('user_profile'), username=user.username)
    else:
        form = UserEditForm(instance=user)
    return render(request, 'crowd_fund_app/user_edit.html', context={'form': form, 'user': user})


def user_password_reset(request, uidb64, token):
    return render(request, 'crowd_fund_app/password_reset_confirm.html', context={'uidb64': uidb64, 'token': token})


def user_password_reset_request(request):
    return render(request, 'crowd_fund_app/password_reset_request.html')


class CustomPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        response = PasswordResetView.post(self, request, *args, **kwargs)
        if response.status_code == http.HTTPStatus.OK:
            return render(request, 'crowd_fund_app/password_reset_completed.html',
                          {'message': response.data.get('detail')},
                          status=response.status_code)
        else:
            return render(request, 'crowd_fund_app/password_reset_completed.html',
                          {'message': str(response.data.get('detail')).join('. Please try again')},
                          status=response.status_code)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    # Catch error responses and redirect to an error page
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if response.status_code != http.HTTPStatus.OK:
            return render(request, 'crowd_fund_app/register_msg.html',
                          {'messages': ['The password reset link is no longer valid. Please, resend a new '
                                        'password reset request']})
        return response

    def post(self, request, *args, **kwargs):
        response = PasswordResetConfirmView.post(self, request, *args, **kwargs)
        if response.status_code == http.HTTPStatus.OK:
            return render(request, 'crowd_fund_app/register_msg.html', {'messages': [response.data.get('detail')]},
                          status=response.status_code)
            return HttpResponse(response.data.get('detail'), status=response.status_code)
        else:
            return render(request, 'crowd_fund_app/register_msg.html', {'messages': [str(response.data.get('detail')).join('. Please try again')]},
                          status=response.status_code)


class DeleteUserView(PasswordResetView):
    serializer_class = CustomUserDeleteSerializer

    def post(self, request, *args, **kwargs):
        response = PasswordResetView.post(self, request, *args, **kwargs)
        if response.status_code == http.HTTPStatus.OK:
            return HttpResponse('Delete confirmation message has been sent to your mail')
        else:
            return HttpResponse(str(response.data.get('detail')).join('. Please try again'),
                                status=response.status_code)


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


def facebook_login(request, access_token, code):
    pass


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class UserProjectsViewSet(ProjectViewSet):
    def get_queryset(self):
        return Project.objects.filter(user_id__id=self.request.user.id)


class CustomEmailConfirmationHMAC(EmailConfirmationHMAC):
    @classmethod
    def from_key(cls, key):
        try:
            # max_age = 60 * 60 * 24 * app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
            # Changed days to one tenth minutes just for testing
            max_age = 10 * app_settings.EMAIL_CONFIRMATION_EXPIRE_DAYS
            pk = signing.loads(key, max_age=max_age, salt=app_settings.SALT)
            ret = CustomEmailConfirmationHMAC(EmailAddress.objects.get(pk=pk, verified=False))
        except (
                signing.SignatureExpired,
                signing.BadSignature,
                EmailAddress.DoesNotExist,
        ):
            ret = None
        return ret


class CustomConfirmEmailView(ConfirmEmailView):

    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            if app_settings.CONFIRM_EMAIL_ON_GET:
                return self.post(*args, **kwargs)
        except Http404:
            self.object = None
        ctx = self.get_context_data()
        print('ctx confirmation: ', ctx.get('confirmation', None))
        if ctx.get('confirmation', None):
            return render(self.request, 'crowd_fund_app/request_activation_link.html')
        return self.render_to_response(ctx)


class TestConfirmEmailView(CustomConfirmEmailView):

    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        emailconfirmation = CustomEmailConfirmationHMAC.from_key(key)
        if not emailconfirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                emailconfirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                raise Http404()
        return emailconfirmation
