from django.core.validators import RegexValidator


def validate_name(value):
    name_validator = RegexValidator(
        regex=r'^[а-яА-Яa-zA-Z\s\-]+$',
        message='Можно использовать только буквы и знак дефис!'
    )
    return name_validator(value)
