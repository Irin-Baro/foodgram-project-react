from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Отображение модели Ingredient в админке."""

    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Отображение модели Tag в админке."""

    list_display = ('id', 'name', 'color', 'slug')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('slug',)


class RecipeIngredientAdmin(admin.TabularInline):
    """Отображение модели RecipeIngredient для RecipeAdmin."""

    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели Recipe в админке."""

    list_display = (
        'id',
        'name',
        'author',
        'display_tags',
        'display_ingredients',
        'get_favorite_count',
    )
    search_fields = ('name', 'ingredients__name')
    list_filter = ('tags', 'name', 'author__username')
    list_display_links = ('name',)
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientAdmin,)

    def get_favorite_count(self, obj):
        return obj.favorites.count()
    get_favorite_count.short_description = 'Число добавлений в избранное'

    def display_ingredients(self, obj):
        return ', '.join([ingredient.name for ingredient
                          in obj.ingredients.all()])
    display_ingredients.short_description = 'Ингредиенты'

    def display_tags(self, obj):
        return ', '.join([tag.name for tag
                          in obj.tags.all()])
    display_tags.short_description = 'Теги'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Отображение модели Favorite в админке."""

    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Отображение модели ShoppingCart в админке."""

    list_display = ('user', 'recipe')
