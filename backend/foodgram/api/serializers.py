from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .fields import (AuthorDefault, CustomBase64ImageField,
                     TagsPrimaryKeyRelatedField, UserToRecipesRelationField)
from recipes.models import (Favourites, Ingredient, IngredientAmount, Recipe,
                            Shopping_cart, Tag)
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
        if type(user) is AnonymousUser:
            return False

        try:
            Subscription.objects.get(user=user, author=obj)
            return True
        except Subscription.DoesNotExist:
            return False


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']
        read_only_fields = ['name', 'measurement_unit']

    def get_name(self, obj):
        return Ingredient.objects.get(id=obj.ingredient.id).name

    def get_measurement_unit(self, obj):
        return Ingredient.objects.get(id=obj.ingredient.id).measurement_unit


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id', 'name', 'color', 'slug']


# class NestedTagSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Tag
#         fields = ['id', 'name', 'color', 'slug']
#         read_only_fields = ['name', 'color', 'slug']
#         extra_kwargs = {
#             'id': {
#                 'read_only': False  # иначе id не дойдут до def create
#             }
#         }


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    # ingredients = IngredientsJSONField()
    tags = TagsPrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = UserRetrieveSerializer(default=serializers.CurrentUserDefault())
    is_favorited = UserToRecipesRelationField(model=Favourites)
    is_in_shopping_cart = UserToRecipesRelationField(model=Shopping_cart)
    image = CustomBase64ImageField()

    # NestedTagSerializer хочет dict, привожу к нему
    # def to_internal_value(self, data):
    #     tags = self.initial_data['tags']
    #     proper_tags = []
    #     for tag in tags:
    #         proper_tag = {'id': tag}
    #         proper_tags.append(proper_tag)
    #     data['tags'] = proper_tags
    #     return super(RecipeSerializer, self).to_internal_value(data)

    # def validate_ingredients(self, ingredients):
    #     if type(ingredients) is not list:
    #         raise serializers.ValidationError(
    #             'Некорректный тип данных для ингредиентов, ожидался list'
    #         )
    #     for ingredient in ingredients:
    #         if type(ingredient) is not dict:
    #             raise serializers.ValidationError(
    #                 'Некорректный тип данных с информацией '
    #                 'о конкретном ингредиенте, ожидался dict'
    #             )
    #         if (
    #             len(ingredient) != 2
    #             or 'id' not in ingredient
    #             or 'amount' not in ingredient
    #         ):
    #             raise serializers.ValidationError(
    #                 'Информация о конкретном ингредиенте '
    #                 'должна содержать 2 поля: id и amount'
    #             )
    #         if type(ingredient['id']) is not int:
    #             raise serializers.ValidationError(
    #                 'Некорректный тип данных для id, ожидался int'
    #             )
    #         try:
    #             Ingredient.objects.get(id=ingredient['id'])
    #         except Ingredient.DoesNotExist:
    #             raise serializers.ValidationError(
    #                 f'Ингредиент с id {ingredient["id"]} не найден'
    #             )
    #         if type(ingredient['amount']) is not int:
    #             raise serializers.ValidationError(
    #                 'Некорректный тип данных для amount, ожидался int'
    #             )

    #         return ingredients

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
        ingredients = validated_data.pop('ingredients')
        # raise BaseException(ingredients[0]['ingredient'])
        # raise BaseException(ingredients[0]['amount'])

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.add(*tags)

        current_ingredients = []
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient']
            amount = ingredient['amount']
            current_ingredient, status = IngredientAmount.objects.get_or_create(  # noqa E501
                ingredient=ingredient_id, amount=amount
            )
            current_ingredients.append(current_ingredient)

        recipe.ingredients.add(*current_ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        # raise BaseException(tags)
        ingredients = validated_data.pop('ingredients')

        # for field in validated_data:
        #     raise BaseException(validated_data)
        recipe = super().update(instance, validated_data)

        recipe.tags.set(tags)

        current_ingredients = []
        for ingredient in ingredients:
            ingredient_id = ingredient['ingredient']
            amount = ingredient['amount']
            current_ingredient, status = IngredientAmount.objects.get_or_create(  # noqa E501
                ingredient=ingredient_id, amount=amount
            )
            # recipe.ingredients.set(current_ingredient)
            current_ingredients.append(current_ingredient)

        recipe.ingredients.set(current_ingredients)

        return recipe


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    author = serializers.HiddenField(default=AuthorDefault())
    email = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
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

    def get_email(self, obj):
        return get_object_or_404(User, id=obj.author.id).email

    def get_id(self, obj):
        return get_object_or_404(User, id=obj.author.id).id

    def get_username(self, obj):
        return get_object_or_404(User, id=obj.author.id).username

    def get_first_name(self, obj):
        return get_object_or_404(User, id=obj.author.id).first_name

    def get_last_name(self, obj):
        return get_object_or_404(User, id=obj.author.id).last_name

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if type(user) is AnonymousUser:
            return False

        try:
            Subscription.objects.get(user=user, author=obj.author)
            return True
        except Subscription.DoesNotExist:
            return False

    def get_recipes(self, obj):
        limit = int(self.context['recipes_limit'])
        # Фильтрация
        qs = Recipe.objects.filter(author=obj.author).values()[:limit]
        # Вывожу только требуемые поля
        result = []
        for i in range(len(qs)):
            obj_dict = {}
            obj_dict['id'] = qs[i]['id']
            obj_dict['name'] = qs[i]['name']
            obj_dict['image'] = qs[i]['image']
            obj_dict['cooking_time'] = qs[i]['cooking_time']
            result.append(obj_dict)
        return result

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()
