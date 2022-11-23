from crowd_fund import settings


def global_settings(request):
    return {
        'DOMAIN': settings.DOMAIN,
        'FACEBOOK_REDIRECT_URL': settings.FACEBOOK_REDIRECT_URL,
    }
