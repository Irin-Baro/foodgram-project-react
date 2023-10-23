from rest_framework import status
from rest_framework.serializers import ValidationError

from recipes.models import Ingredient


def validate_subscription(self, data):
    author = self.instance
    user = self.context.get('request').user
    if user.subscriber.filter(author=author).exists():
        raise ValidationError(
            {'errors': 'Вы уже подписаны на этого пользователя!'},
            code=status.HTTP_400_BAD_REQUEST,
        )
    if user == author:
        raise ValidationError(
            {'errors': 'Нельзя подписаться на самого себя!'},
            code=status.HTTP_400_BAD_REQUEST,
        )
    return data


def validate_tags_ingredients(self, data):
    tags = data.get('tags')
    if not tags:
        raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег!'})
    unique_tags = set()
    for tag in tags:
        if tag in unique_tags:
            raise ValidationError({'tags': f'Тег {tag} уже выбран!'})
        unique_tags.add(tag)

    ingredients = data.get('recipe_ingredients')
    if not ingredients:
        raise ValidationError(
            {'ingredients': 'Нужно добавить хотя бы один ингредиент!'}
        )
    unique_ingredients = set()
    for ingredient in ingredients:
        ingredient_id = ingredient['ingredient'].get('id')
        if ingredient_id in unique_ingredients:
            raise ValidationError(
                {'ingredient_id': f'Ингредиент с id {ingredient_id} '
                                  'уже добавлен!'}
            )
        try:
            Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist:
            raise ValidationError(
                {'ingredient_id': f'Ингредиента с id {ingredient_id} нет!'}
            )
        unique_ingredients.add(ingredient_id)
    return data


def validate_image(value):
    if not value:
        raise ValidationError('Нужно прикрепить картинку!')
    return value


def validate_amount(value):
    if value <= 0:
        raise ValidationError('Количество ингредиента должно быть больше 0!')
    return value


def validate_cooking_time(value):
    if value <= 0:
        raise ValidationError('Время приготовления должно быть больше 0!')
    return value
