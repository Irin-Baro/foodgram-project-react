from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserSerializer,
    RecipeCreateSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SmallRecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from users.models import Subscription, User


class CustomUserViewSet(UserViewSet):
    """Представление пользователей."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    filterset_fields = ('username',)

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                author=author
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Вы не подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPagination
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            SubscriptionSerializer(
                self.paginate_queryset(
                    User.objects.filter(subscribing__user=request.user)
                ),
                many=True,
                context={'request': request}
            ).data
        )


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_permissions(self):
        if self.action in ('create',):
            return (IsAuthenticated(),)
        if self.action in ('update', 'partial_update', 'destroy'):
            return (IsAuthorOrReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe(self, model, user, pk):
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'errors': 'Такого рецепта нет'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if model.objects.filter(recipe=recipe, user=user).exists():
            return Response(
                {'errors': 'Рецепт уже был добавлен'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.create(user=user, recipe=recipe)
        return Response(
            SmallRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def delete_recipe(self, model, user, pk):
        obj = model.objects.filter(
            user=user,
            recipe=get_object_or_404(Recipe, id=pk)
        )
        if obj:
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепта нет или уже удален'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def handle_recipe(self, request, pk=None, model=None):
        if request.method == 'POST':
            return self.add_recipe(model, request.user, pk)
        else:
            return self.delete_recipe(model, request.user, pk)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated, IsAuthorOrReadOnly)
    )
    def favorite(self, request, pk=None):
        return self.handle_recipe(request, pk, Favorite)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated, IsAuthorOrReadOnly)
    )
    def shopping_cart(self, request, pk=None):
        return self.handle_recipe(request, pk, ShoppingCart)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = ShoppingCart.objects.filter(
            user=request.user
        ).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(amount=Sum('recipe__recipe_ingredients__amount'))

        shopping_cart = {}
        for ingredient in ingredients:
            name = ingredient['recipe__ingredients__name']
            measurement_unit = ingredient[
                'recipe__ingredients__measurement_unit'
            ]
            amount = ingredient['amount']

            key = f'{name} ({measurement_unit})'
            if key in shopping_cart:
                shopping_cart[key] += amount
            else:
                shopping_cart[key] = amount

        final_shopping_cart = [f'• {key} - {value}'
                               for key, value in shopping_cart.items()]

        response = HttpResponse('\n'.join(final_shopping_cart),
                                content_type='text/plain')
        response['Content-Disposition'] = ('attachment; '
                                           'filename=shopping-list.txt')
        return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
