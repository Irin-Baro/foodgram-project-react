from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    """Фильтрация рецептов по тегам, автору, избранному и списку покупок."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = filters.CharFilter(
        field_name='author__id',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_by_relation(self, queryset, relation, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(**{relation: user})
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        return self.filter_by_relation(
            queryset, 'users_favorite_recipes', value
        )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.filter_by_relation(
            queryset, 'users_shopping_cart_recipes', value
        )
