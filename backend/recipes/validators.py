from django.core.validators import MinValueValidator, RegexValidator

from ..core import constants


def validate_color(value):
    color_validator = RegexValidator(
        regex=r'^#([A-Fa-f0-9]{3,6})$',
        message='Введенное значение не соответствует формату HEX!'
    )
    return color_validator(value)


def validate_tag_name(value):
    name_validator = RegexValidator(
        regex=r'^[а-яА-Яa-zA-ZёЁ]+$',
        message='Можно использовать только буквы!'
    )
    return name_validator(value)


def validate_ingredient_name(value):
    ingredient_name_validator = RegexValidator(
        regex=r'^[а-яА-Яa-zA-Z0-9ёЁ\s\-\(\)\"\'«»%]+$',
        message=('Можно использовать только буквы, цифры, скобки, '
                 'знаки дефис, кавычки и проценты!')
    )
    return ingredient_name_validator(value)


def validate_recipe_name(value):
    recipe_name_validator = RegexValidator(
        regex=r'^[а-яА-Яa-zA-ZёЁ\s\-\(\)\"\'«»]+$',
        message=('Можно использовать только буквы, скобки, '
                 'знаки дефис и кавычки!')
    )
    return recipe_name_validator(value)


def validate_cooking_time(value):
    cooking_time_validator = MinValueValidator(
        constants.MIN_VALUE_COOKING_TIME,
        message='Минимальное время приготовления: 1 минута!'
    )
    return cooking_time_validator(value)


def validate_amount(value):
    amount_validator = MinValueValidator(
        constants.MIN_VALUE_INGREDIENT_AMOUNT,
        message='Минимальное количество ингредиентов: 1!'
    )
    return amount_validator(value)
