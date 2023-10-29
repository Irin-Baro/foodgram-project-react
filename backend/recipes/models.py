from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from . import constants
from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=constants.MAX_TAG_NAME_LENGTH,
        unique=True,
        verbose_name='Название тега',
        help_text='Укажите название тега',
    )
    color = models.CharField(
        unique=True,
        max_length=constants.MAX_TAG_COLOR_LENGTH,
        validators=(
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не соответствует формату HEX!'
            ),
        ),
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
        validators=(
            MinValueValidator(
                constants.MIN_VALUE_COOKING_TIME,
                message='Минимальное время: 1 минута!'
            ),
        ),
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

    @property
    def ingredients(self):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=self)
        return [
            (recipe_ingredient.ingredient, recipe_ingredient.amount)
            for recipe_ingredient in recipe_ingredients
        ]


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
        validators=(
            MinValueValidator(
                constants.MIN_VALUE_INGREDIENT_AMOUNT,
                message='Минимальное количество: 1!'
            ),
        ),
        verbose_name='Количество',
        help_text='Укажите количество ингредиента в рецепте',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name}: {self.amount}'
