from django.db import models

from core import constants
from users.models import User
from . import validators


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=constants.MAX_TAG_NAME_LENGTH,
        validators=(validators.tag_name_validator,),
        unique=True,
        verbose_name='Название тега',
        help_text='Укажите название тега',
    )
    color = models.CharField(
        unique=True,
        max_length=constants.MAX_TAG_COLOR_LENGTH,
        validators=(validators.color_validator,),
        verbose_name='Цветовой HEX-код',
        help_text='Укажите цветовой HEX-код',
    )
    slug = models.SlugField(
        max_length=constants.MAX_TAG_SLUG_LENGTH,
        unique=True,
        verbose_name='Уникальный слаг',
        help_text='Укажите уникальный слаг',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=constants.MAX_INGREDIENT_NAME_LENGTH,
        validators=(validators.ingredient_name_validator,),
        db_index=True,
        verbose_name='Название ингредиента',
        help_text='Укажите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=constants.MAX_MEASUREMENT_UNIT_LENGTH,
        verbose_name='Единицы измерения',
        help_text='Укажите единицы измерения ингредиента',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredients'
            ),
        )
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Укажите автор рецепта',
    )
    name = models.CharField(
        max_length=constants.MAX_RECIPE_NAME_LENGTH,
        validators=(validators.recipe_name_validator,),
        db_index=True,
        verbose_name='Название рецепта',
        help_text='Укажите название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        verbose_name='Картинка',
        help_text='Прикрепите картинку',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Выберите теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(validators.cooking_time_validator,),
        verbose_name='Время приготовления (в минутах)',
        help_text='Укажите время приготовления',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель ингридиентов рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт',
        help_text='Укажите рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(validators.amount_validator,),
        verbose_name='Количество',
        help_text='Укажите количество ингредиента в рецепте',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe'
            ),
        )
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name}: {self.amount}'
