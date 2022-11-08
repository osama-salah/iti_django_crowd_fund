from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_redirect_url(self, request):
        return reverse('email_confirmed')
