import re

from django.core.exceptions import ValidationError


def validate_color(value):
    """Валидация цветового HEX-кода."""
    if len(value) != 7:
        raise ValidationError('Должно быть 7 символов!')
    used_wrong_chars = ''.join(set(re.sub(r'^#([A-Fa-f0-9]{6})$', '', value)))
    if used_wrong_chars:
        raise ValidationError(f'Нельзя использовать: {used_wrong_chars}')
    return value
