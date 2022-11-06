import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework.authtoken.models import Token as CustomToken

from crowd_fund import settings


def mobile_validator(mobile):
    if not re.fullmatch(r'01[0125]\d{8}', mobile):
        raise ValidationError(f'${mobile} is not a valid mobile number')


class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=11, validators=[mobile_validator])
    picture = models.ImageField(null=True, upload_to='crowd_fund_app/images/users/', max_length=500)
    status = models.CharField(max_length=9, choices=[
        ('inactive', 'Inactive'),       # Inactivated by an admin or timeout
        ('pending', 'Pending'),         # Hasn't activated his account yet
        ('active', 'Active'),           # Activated
        ('suspended', 'Suspended'),     # Banned
    ], default='pending')
    birthdate = models.DateField(null=True, blank=True)
    facebook_profile = models.URLField(max_length=500, null=True, blank=True)
    with open(f'{settings.BASE_DIR}/crowd_fund_app/static/crowd_fund_app/documents/countries.txt') as f:
        country = models.CharField(null=True, blank=True, choices=[(c[:-1], c[:-1]) for c in f.readlines()], max_length=50)


class Token(CustomToken):
    key = models.CharField("Key", max_length=40, db_index=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name="User",
    )
