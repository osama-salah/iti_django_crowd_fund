import http
import os

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import url_str_to_user_pk, user_pk_to_url_str, user_username
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.utils import build_absolute_uri
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from crowd_fund_app.forms import UserEditForm
from crowd_fund_app.models import CustomUser
from crowd_fund_app.serializers import CustomUserDeleteSerializer


# This view sends a message to current user's registered email
def user_delete_direct(request):
    # This part of code is taken from dj-rest-auth.serializers.PasswordResetSerializer.save and
    # dj-rest-auth.forms.AllAuthPasswordResetForm.save
    current_site = get_current_site(request)
    user = request.user
    email = user.email
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
    return HttpResponse('Delete confirmation message has been sent to your mail')


# This view shows an email field to send the message to
def user_delete(request, uidb64, token):
    uid = url_str_to_user_pk(uidb64)
    try:
        user = CustomUser.objects.get(pk=uid)
        if not default_token_generator.check_token(user, token):
            raise ValidationError({'token': ['Invalid value']})
        username = user.username
        user.delete()
        return HttpResponse(f'User {username} deleted successfully')
    except ValidationError:
        return HttpResponse('Expired or invalid token')
    except ValueError:
        pass
    return HttpResponse('User not found')


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
                    os.remove(original_picture_path)
                except FileNotFoundError:
                    pass
            user = form.save()
            return redirect('/dj-rest-auth/user', username=user.username)
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
            return HttpResponse(response.data.get('detail'), status=response.status_code)
        else:
            return HttpResponse(str(response.data.get('detail')).join('. Please try again'),
                                status=response.status_code)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    # Catch error responses and redirect to an error page
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        if response.status_code != http.HTTPStatus.OK:
            return HttpResponse('The password reset link is no longer valid. Please, resend a new '
                                'password reset request')
        return response

    def post(self, request, *args, **kwargs):
        response = PasswordResetConfirmView.post(self, request, *args, **kwargs)
        if response.status_code == http.HTTPStatus.OK:
            print('OK')
            return HttpResponse(response.data.get('detail'), status=response.status_code)
        else:
            print('Not OK')
            return HttpResponse(str(response.data.get('detail')).join('. Please try again'),
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


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
