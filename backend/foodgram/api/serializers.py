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


class NestedTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['color', 'slug']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientsJSONField()
    tags = NestedTagSerializer(many=True)
    author = UserRetrieveSerializer(default=serializers.CurrentUserDefault())
    is_favorited = UserToRecipesRelationField(model=Favourites)
    is_in_shopping_cart = UserToRecipesRelationField(model=Shopping_cart)
    image = CustomBase64ImageField()

    # Вложенный сериализатор хочет dict, привожу к нему
    def to_internal_value(self, data):
        tags = self.initial_data['tags']
        proper_tags = []
        for tag in tags:
            # Почему-то если указать id, то оно не сохраняется в validated_data
            # validated_data.tags будет пустым OrderedDict внутри метода create
            # Поэтому сохраняю id через name
            proper_tag = {'name': tag}
            proper_tags.append(proper_tag)
        data['tags'] = proper_tags
        return super(RecipeSerializer, self).to_internal_value(data)

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

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        # raise BaseException(tags)

        recipe = Recipe.objects.create(**validated_data)

        for tag in tags:
            # вытаскиваю id из name
            current_tag = Tag.objects.get(
                id=tag['name']
            )

            recipe.tags.add(current_tag)
        return recipe

    # def update(self, instance, validated_data):
    #     pass
