from rest_framework import serializers

from recipes.models import Ingredient, Recipe, Tag
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
    ingredients = serializers.JSONField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserRetrieveSerializer(default=serializers.CurrentUserDefault())

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
                or 'id' not in ingredient.keys()
                or 'amount' not in ingredient.keys()
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
            'name', 'image', 'text', 'cooking_time'
        ]

        read_only_fields = ['id', 'author']
