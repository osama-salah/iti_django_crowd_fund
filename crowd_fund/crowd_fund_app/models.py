import re

from django.db import models
from django.core.exceptions import ValidationError


def mobile_validator(mobile):
    if not re.fullmatch(r'01[0125]\d{8}', mobile):
        raise ValidationError(f'${mobile} is not a valid mobile number')


class User(models.Model):
    name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)
    mobile = models.CharField(max_length=11, validators=[mobile_validator])
    picture = models.ImageField(null=True, upload_to='crowd_fund_app/static/crowd_fund_app/images/')
    status = models.Choices([
        ('inactive', 'Inactive'),       # Inactivated by an admin or timeout
        ('pending', 'Pending'),         # Hasn't activated his account yet
        ('active', 'Active'),           # Activated
        ('suspended', 'Suspended'),     # Banned
    ])
    # projects = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    # donations = models.ForeignKey(Donation, on_delete=models., null=True)

