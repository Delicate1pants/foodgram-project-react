import re

from django.core.exceptions import ValidationError


def hex_code_validator(string):
    val_err = 'Invalid hex color code'

    if string is None:
        raise ValidationError(val_err)

    regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"

    pattern = re.compile(regex)

    if re.search(pattern, str):
        return

    raise ValidationError(val_err)
