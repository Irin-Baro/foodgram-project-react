from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import Subscription, User
from .filters import RecipeFilter
from .pagination import Pagination
from .permissions import ActionPermissions, IsAuthorOrReadOnly
from .serializers import (UserSerializer,
                          IngredientSerializer,
                          RecipeCreateSerializer,
                          RecipeSerializer,
                          SmallRecipeSerializer,
                          SubscriptionSerializer,
                          TagSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Представление пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('username',)
    filterset_fields = ('username',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return UserSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        if self.action in ('subscribe', 'subscriptions'):
            return SubscriptionSerializer
        return UserCreateSerializer

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('post',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response('Пароль успешно изменен.',
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated,),
        pagination_class=Pagination
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, id=pk)
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
        pagination_class=Pagination
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
    pagination_class = Pagination
    permission_classes = (ActionPermissions,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def add_recipe(self, relation, user, pk):
        try:
            recipe = get_object_or_404(Recipe, id=pk)
        except Exception:
            return Response(
                {'errors': 'Такого рецепта нет'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if getattr(user, relation).filter(id=pk).exists():
            return Response(
                {'errors': 'Рецепт уже был добавлен'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        getattr(user, relation).add(recipe)
        user.shopping_cart_recipes.add(recipe)
        return Response(
            SmallRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def delete_recipe(self, relation, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if not getattr(user, relation).filter(id=pk).exists():
            return Response(
                {'errors': 'Рецепт не был добавлен в корзину покупок'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        getattr(user, relation).remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def handle_recipe(self, request, pk=None, relation=None):
        if request.method == 'POST':
            return self.add_recipe(relation, request.user, pk)
        else:
            return self.delete_recipe(relation, request.user, pk)

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated, IsAuthorOrReadOnly)
    )
    def favorite(self, request, pk):
        return self.handle_recipe(request, pk, 'favorite_recipes')

    @action(
        methods=('post', 'delete'),
        detail=True,
        permission_classes=(IsAuthenticated, IsAuthorOrReadOnly)
    )
    def shopping_cart(self, request, pk):
        return self.handle_recipe(request, pk, 'shopping_cart_recipes')

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__users_shopping_cart_recipes=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_cart = {}
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
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
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    filterset_fields = ('name',)
    permission_classes = (AllowAny,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
