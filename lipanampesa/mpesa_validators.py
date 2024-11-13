from enum import Enum
from django.core.exceptions import ValidationError
from phonenumber_field.phonenumber import to_python
from phonenumbers.phonenumberutil import is_possible_number


def validate_possible_number(phone, country=None):
    phone = to_python(phone, country)
    if (
        phone
        and not is_possible_number(phone)
        or not phone.is_valid()
    ):
        raise ValidationError("Invalid phone number")
    return phone