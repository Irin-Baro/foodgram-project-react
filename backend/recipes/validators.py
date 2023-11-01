from django.core.validators import MinValueValidator, RegexValidator

from core import constants


color_validator = RegexValidator(
    regex=r'^#([A-Fa-f0-9]{3,6})$',
    message='Введенное значение не соответствует формату HEX!'
)

tag_name_validator = RegexValidator(
    regex=r'^[а-яА-Яa-zA-ZёЁ]+$',
    message='Можно использовать только буквы!'
)

ingredient_name_validator = RegexValidator(
    regex=r'^[а-яА-Яa-zA-Z0-9ёЁ\s\-\(\)\"\'«»%]+$',
    message=('Можно использовать только буквы, цифры, скобки, '
             'знаки дефис, кавычки и проценты!')
)

recipe_name_validator = RegexValidator(
    regex=r'^[а-яА-Яa-zA-ZёЁ\s\-\(\)\"\'«»]+$',
    message=('В названии рецепта можно использовать только буквы, скобки, '
             'знаки дефис и кавычки!')
)

cooking_time_validator = MinValueValidator(
    constants.MIN_VALUE_COOKING_TIME,
    message='Минимальное время приготовления: 1 минута!'
)

amount_validator = MinValueValidator(
    constants.MIN_VALUE_INGREDIENT_AMOUNT,
    message='Минимальное количество ингредиентов: 1!'
)
