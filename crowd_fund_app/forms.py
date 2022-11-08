from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str, user_username
from allauth.utils import build_absolute_uri
from dj_rest_auth.forms import AllAuthPasswordResetForm
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from crowd_fund_app.models import CustomUser


class UserDeleteForm(AllAuthPasswordResetForm):
    def save(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.cleaned_data['email']
        token_generator = kwargs.get('token_generator', default_token_generator)

        for user in self.users:

            temp_key = token_generator.make_token(user)

            # send the password reset email
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
            get_adapter(request).send_mail(
                'account/email/user_delete_key', email, context
            )
        return self.cleaned_data['email']


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Retype password", widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = ("username", "first_name", "last_name", "email", "mobile", "picture")


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "mobile", "picture", "birthdate",
                  "facebook_profile", "country")

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
