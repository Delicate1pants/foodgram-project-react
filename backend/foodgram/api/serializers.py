from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject

from .fields import AuthorDefault, CustomBase64ImageField, RecipeDefault
from .utils import ingr_amount_bulk_create_plus
from recipes.models import (Favourite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        ]

        read_only_fields = ['id']

        extra_kwargs = {
            'password': {
                'write_only': True,
            },
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserRetrieveSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        ]

        read_only_fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False

        return Subscription.objects.filter(user=user, author=obj).exists()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    name = serializers.CharField(
        source='ingredient.name', read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']
        read_only_fields = ['name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id', 'name', 'color', 'slug']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserRetrieveSerializer(default=serializers.CurrentUserDefault())
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = CustomBase64ImageField(use_url=True)

    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(
                attribute, PKOnlyObject
            ) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                # Мой код про тэги, остальное взято у родителя
                if field.field_name == 'tags':
                    serializer = TagSerializer(attribute, many=True)
                    ret[field.field_name] = list(serializer.data)
                else:
                    ret[field.field_name] = field.to_representation(attribute)

        return ret

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        ]

        read_only_fields = [
            'id', 'author', 'is_favorited', 'is_in_shopping_cart'
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False

        return Favourite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False

        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def validate(self, data):
        tags = data.get('tags')
        ingrs = data.get('ingredients')

        tags_are_not_unique = len(set(tags)) < len(tags)

        ingr_ids = []
        for ingr in ingrs:
            ingr_ids.append(ingr['ingredient'])

        ingr_ids_are_not_unique = len(set(ingr_ids)) < len(ingr_ids)

        if tags_are_not_unique:
            raise serializers.ValidationError(
                'Тэги не должны содержать повторяющиеся id'
            )
        if ingr_ids_are_not_unique:
            raise serializers.ValidationError(
                'Ингредиенты не должны содержить повторяющиеся id'
            )
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        return ingr_amount_bulk_create_plus(ingredients, recipe)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')

        recipe = super().update(instance, validated_data)

        return ingr_amount_bulk_create_plus(ingredients, recipe)


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.HiddenField(default=AuthorDefault())
    email = serializers.EmailField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(
        source='author.first_name', read_only=True
    )
    last_name = serializers.CharField(
        source='author.last_name', read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'user', 'author', 'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        ]
        read_only_fields = [
            'user', 'author', 'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False

        return Subscription.objects.filter(
            user=user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        # Фильтрация
        limit = self.context['recipes_limit']
        if limit is not None:
            limit = int(limit)
            qs = Recipe.objects.filter(
                author=obj.author
            ).order_by('-id').values()[:limit]
        else:
            qs = Recipe.objects.filter(
                author=obj.author
            ).order_by('-id').values()

        return qs.values('id', 'name', 'image', 'cooking_time')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        author = data.get('author')
        user = data.get('user')

        if author == user:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя'
            )
        if Subscription.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError('Подписка уже оформлена')
        return data


class FavouritesSerializer(serializers.ModelSerializer):
    already_related_error_msg = 'Рецепт уже есть в избранном'
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.HiddenField(default=RecipeDefault())
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = CustomBase64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        model = Favourite
        fields = [
            'user', 'recipe', 'id', 'name', 'image',
            'cooking_time'
        ]

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')

        # Такое написание нужно, чтобы для наследника тоже работало
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                self.already_related_error_msg
            )
        return data


class ShoppingCartSerializer(FavouritesSerializer):
    already_related_error_msg = 'Рецепт уже есть в списке покупок'

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe', 'id', 'name', 'image', 'cooking_time']
