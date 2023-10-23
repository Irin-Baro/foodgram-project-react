from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User
from .validators import (
    validate_amount,
    validate_cooking_time,
    validate_image,
    validate_subscription,
    validate_tags_ingredients,
)


def has_user_relation(self, obj, relation):
    user = self.context.get('request').user
    return user.is_authenticated and relation.filter(user=user).exists()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return has_user_relation(self, obj, obj.subscribing)


class SmallRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор вывода нескольких полей рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор подписки/отписки."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        return validate_subscription(self, data)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = recipes[: int(recipes_limit)]
        return SmallRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента в рецепте."""

    id = serializers.IntegerField(
        source='ingredient.id',
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    amount = serializers.IntegerField(
        validators=(validate_amount,),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    tags = TagSerializer(
        many=True,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(
        required=True,
        validators=(validate_image,),
    )
    cooking_time = serializers.IntegerField(
        validators=(validate_cooking_time,),
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        return has_user_relation(self, obj, obj.favorites)

    def get_is_in_shopping_cart(self, obj):
        return has_user_relation(self, obj, obj.shoppingcarts)


class RecipeCreateSerializer(RecipeSerializer):
    """Сериализатор создания/редактирования рецепта."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )

    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields
        validators = (
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('author', 'name'),
                message='Вы уже разместили рецепт с таким названием'
            ),
        )

    def validate(self, data):
        return validate_tags_ingredients(self, data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            Tag.objects.filter(
                id__in=instance.tags.all().values_list('id', flat=True)
            ),
            many=True,
        ).data
        return representation

    def add_tags(self, tags_data, recipe):
        recipe.tags.add(*[Tag.objects.get(id=tag.id) for tag in tags_data])

    def add_ingredients(self, ingredients_data, recipe):
        [RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=Ingredient.objects.get(
                id=ingredient_data['ingredient']['id']
            ),
            amount=ingredient_data['amount'],
        ) for ingredient_data in ingredients_data]

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        ingredients_data = validated_data.pop('recipe_ingredients')
        instance.ingredients.clear()
        self.add_ingredients(ingredients_data, instance)
        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        self.add_tags(tags_data, instance)
        instance.save()
        return instance
