import re

from django.core.exceptions import ValidationError


def validate_name(value):
    """Валидация имени и фамилии пользователя."""
    used_wrong_chars = ''.join(
        set(re.sub(r'^[а-яА-Яa-zA-Z0-9\s]+$', '', value))
    )
    if used_wrong_chars:
        raise ValidationError(f'Нельзя использовать: {used_wrong_chars}')
    return value
