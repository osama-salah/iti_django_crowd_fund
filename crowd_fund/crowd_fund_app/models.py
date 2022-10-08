import re

from django.db import models
from django.core.exceptions import ValidationError


def mobile_validator(mobile):
    if not re.fullmatch(r'01[0125]\d{8}', mobile):
        raise ValidationError(f'${mobile} is not a valid mobile number')


def greater_than_zero_validator(value):
    if value <= 0:
        raise ValidationError(f'${value} must be greater than zero')


class User(models.Model):
    name = models.CharField(max_length=25, primary_key=True)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    mobile = models.CharField(max_length=11, validators=[mobile_validator])
    picture = models.ImageField(null=True, upload_to='crowd_fund_app/media/crowd_fund_app/images/users/')
    status = models.CharField(max_length=9, choices=[
        ('inactive', 'Inactive'),       # Inactivated by an admin or timeout
        ('pending', 'Pending'),         # Hasn't activated his account yet
        ('active', 'Active'),           # Activated
        ('suspended', 'Suspended'),     # Banned
    ])


class ProjectCategory(models.Model):
    name = models.CharField(max_length=16)


class ProjectTags(models.Model):
    name = models.CharField(max_length=32)


class Project(models.Model):
    title = models.CharField(max_length=64, null=False)
    details = models.TextField(max_length=1024)
    category = models.ManyToManyField(to=ProjectCategory, related_name='projects')
    user = models.ManyToManyField(to=User, related_name='projects')
    total_target = models.FloatField(null=False, validators=[greater_than_zero_validator])
    tags = models.ManyToManyField(to=ProjectTags, related_name='projects')
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    added_at = models.DateTimeField(auto_now_add=True)


class Donation(models.Model):
    user = models.OneToOneField(to=User, related_name='donations', on_delete=models.CASCADE)
    project = models.OneToOneField(to=Project, related_name='donations', on_delete=models.CASCADE)
    amount = models.FloatField(null=False, validators=[greater_than_zero_validator])
    date = models.DateTimeField(auto_now_add=True)


class Image(models.Model):
    file = models.ImageField(null=True, upload_to='crowd_fund_app/media/crowd_fund_app/images/projects/')
    project = models.ManyToManyField(to=Project, related_name='images')
