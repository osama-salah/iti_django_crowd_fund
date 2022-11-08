import re

from django.core.exceptions import ValidationError


def greater_than_zero_validator(value):
    if value <= 0:
        raise ValidationError(f'${value} must be greater than zero')


def mobile_validator(mobile):
    if not re.fullmatch(r'01[0125]\d{8}', mobile):
        raise ValidationError(f'${mobile} is not a valid mobile number')