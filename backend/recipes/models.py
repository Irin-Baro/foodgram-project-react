from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

from .validators import validate_color


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='Название тега',
        help_text='Укажите название тега',
    )
    color = models.CharField(
        unique=True,
        null=True,
        blank=True,
        max_length=7,
        validators=(validate_color,),
        verbose_name='Цветовой HEX-код',
        help_text='Укажите цветовой HEX-код',
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        blank=True,
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
        max_length=150,
        db_index=True,
        verbose_name='Название ингредиента',
        help_text='Укажите название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=150,
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
        max_length=200,
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
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Список ингредиентов',
        help_text='Выберите ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Выберите теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1, message='Минимальное время: 1 минута!'),
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


class RecipeIngredient(models.Model):
    """Модель ингридиентов рецепта."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
        help_text='Укажите рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
        help_text='Укажите ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(1, message='Минимальное количество: 1!'),
        ),
        verbose_name='Количество',
        help_text='Укажите количество ингредиента в рецепте',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name}: {self.amount}'


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Укажите пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Выберите рецепт',
    )

    class Meta:
        abstract = True
        ordering = ('-id',)
        default_related_name = '%(class)ss'


class ShoppingCart(UserRecipe):
    """Модель корзины покупок."""

    class Meta(UserRecipe.Meta):
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe_in_cart'
            ),
        )
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    def __str__(self):
        return f'{self.user.username} добавил в список покупок {self.recipe}'


class Favorite(UserRecipe):
    """Модель избранного рецепта."""

    class Meta(UserRecipe.Meta):
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite_recipe'
            ),
        )
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe}'
