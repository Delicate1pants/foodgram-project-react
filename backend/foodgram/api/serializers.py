from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers

from .fields import (CustomBase64ImageField, IngredientsJSONField,
                     TagsPrimaryKeyRelatedField, UserToRecipesRelationField)
from recipes.models import Favourites, Ingredient, Recipe, Shopping_cart, Tag
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
        author = self.context['request'].user
        if type(author) is AnonymousUser:
            return False

        try:
            Subscription.objects.get(user=obj, author=author)
            return True
        except Subscription.DoesNotExist:
            return False


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id', 'name', 'color', 'slug']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsJSONField()
    tags = TagsPrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserRetrieveSerializer(default=serializers.CurrentUserDefault())
    is_favorited = UserToRecipesRelationField(model=Favourites)
    is_in_shopping_cart = UserToRecipesRelationField(model=Shopping_cart)
    image = CustomBase64ImageField()

    def validate_ingredients(self, ingredients):
        if type(ingredients) is not list:
            raise serializers.ValidationError(
                'Некорректный тип данных для ингредиентов, ожидался list'
            )
        for ingredient in ingredients:
            if type(ingredient) is not dict:
                raise serializers.ValidationError(
                    'Некорректный тип данных с информацией '
                    'о конкретном ингредиенте, ожидался dict'
                )
            if (
                len(ingredient) != 2
                or 'id' not in ingredient
                or 'amount' not in ingredient
            ):
                raise serializers.ValidationError(
                    'Информация о конкретном ингредиенте '
                    'должна содержать 2 поля: id и amount'
                )
            if type(ingredient['id']) is not int:
                raise serializers.ValidationError(
                    'Некорректный тип данных для id, ожидался int'
                )
            try:
                Ingredient.objects.get(id=ingredient['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f'Ингредиент с id {ingredient["id"]} не найден'
                )
            if type(ingredient['amount']) is not int:
                raise serializers.ValidationError(
                    'Некорректный тип данных для amount, ожидался int'
                )

        return ingredients

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

    # def get_is_favorited(self, obj):
    #     user = self.context['request'].user

    #     try:
    #         favourites = Favourites.objects.get(user=user)
    #         if obj in favourites.recipes:
    #             return True
    #         return False
    #     except Favourites.DoesNotExist:
    #         return False

    # def get_is_in_shopping_cart(self, obj):
    #     user = self.context['request'].user

    #     try:
    #         shopping_cart = Shopping_cart.objects.get(user=user)
    #         if obj in shopping_cart.recipes:
    #             return True
    #         return False
    #     except Shopping_cart.DoesNotExist:
    #         return False
