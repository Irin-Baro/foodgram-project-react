import re

from django.core.exceptions import ValidationError


def validate_username(value):
    """Валидация имени пользователя."""
    if value in ('me',):
        raise ValidationError(f'Нельзя использовать {value} как юзернейм!')
    used_wrong_chars = ''.join(set(re.sub(r'^[\w.@+-]+', '', value)))
    if used_wrong_chars:
        raise ValidationError(f'Нельзя использовать: {used_wrong_chars}')
    return value
