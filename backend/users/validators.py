from django.core.validators import RegexValidator


name_validator = RegexValidator(
    regex=r'^[а-яА-Яa-zA-Z\s\-]+$',
    message='Можно использовать только буквы и знак дефис!'
)
