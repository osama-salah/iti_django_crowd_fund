import re

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token as CustomToken

import crowd_fund_app
from crowd_fund import settings


def mobile_validator(mobile):
    if not re.fullmatch(r'01[0125]\d{8}', mobile):
        raise ValidationError(f'${mobile} is not a valid mobile number')


def greater_than_zero_validator(value):
    if value <= 0:
        raise ValidationError(f'${value} must be greater than zero')


class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=11, validators=[mobile_validator])
    picture = models.ImageField(null=True, upload_to='crowd_fund_app/media/crowd_fund_app/images/users/')
    status = models.CharField(max_length=9, choices=[
        ('inactive', 'Inactive'),       # Inactivated by an admin or timeout
        ('pending', 'Pending'),         # Hasn't activated his account yet
        ('active', 'Active'),           # Activated
        ('suspended', 'Suspended'),     # Banned
    ], default='pending')
    birthdate = models.DateField(null=True, blank=True)
    facebook_profile = models.URLField(max_length=100, null=True, blank=True)
    with open(f'{settings.BASE_DIR}/crowd_fund_app/static/crowd_fund_app/documents/countries.txt') as f:
        country = models.CharField(null=True, blank=True, choices=[(c[:-1], c[:-1]) for c in f.readlines()], max_length=50)


class ProjectCategory(models.Model):
    name = models.CharField(max_length=16)


class ProjectTags(models.Model):
    name = models.CharField(max_length=32)


class Project(models.Model):
    title = models.CharField(max_length=64, null=False)
    details = models.TextField(max_length=1024)
    category = models.ManyToManyField(to=ProjectCategory, related_name='projects')
    user = models.ManyToManyField(to=CustomUser, related_name='projects')
    total_target = models.FloatField(null=False, validators=[greater_than_zero_validator])
    tags = models.ManyToManyField(to=ProjectTags, related_name='projects')
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    added_at = models.DateTimeField(auto_now_add=True)


class Donation(models.Model):
    user = models.OneToOneField(to=CustomUser, related_name='donations', on_delete=models.CASCADE)
    project = models.OneToOneField(to=Project, related_name='donations', on_delete=models.CASCADE)
    amount = models.FloatField(null=False, validators=[greater_than_zero_validator])
    date = models.DateTimeField(auto_now_add=True)


class Image(models.Model):
    file = models.ImageField(null=True, upload_to='crowd_fund_app/media/crowd_fund_app/images/projects/')
    project = models.ManyToManyField(to=Project, related_name='images')


class Token(CustomToken):
    key = models.CharField("Key", max_length=40, db_index=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name="User",
    )