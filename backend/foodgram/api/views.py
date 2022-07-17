from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import utils
from djoser.conf import settings
from djoser.views import TokenCreateView as DjoserTokenCreateView
from rest_framework import filters, mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filtersets import RecipeFilterSet
from .pagination import IngredientListPagination, ListPagination
from .permissions import HasAccessOrReadOnly
from .serializers import (FavouritesSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)
from recipes.models import Favourites, Ingredient, Recipe, Shopping_cart, Tag
from users.models import Subscription, User


class TokenCreateView(DjoserTokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    pagination_class = IngredientListPagination


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    queryset = Recipe.objects.all().order_by('-id')
    serializer_class = RecipeSerializer
    permission_classes = (HasAccessOrReadOnly,)
    pagination_class = ListPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SubscriptionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = Subscription.objects.filter(user=request.user)
        pagination = ListPagination()
        final_qs = pagination.paginate_queryset(
            queryset=queryset, request=request
        )
        serializer = self.serializer_class(
            final_qs, many=True, context={
                'request': request,
                'recipes_limit': self.request.query_params.get('recipes_limit')
            }
        )
        return pagination.get_paginated_response(
            data=serializer.data
        )

    def create(self, request, author_id=None):
        serializer = self.serializer_class(
            data=request.data, context={
                'request': request, 'author_id': author_id,
                'recipes_limit': self.request.query_params.get('recipes_limit')
            }
        )
        serializer.is_valid(raise_exception=True)
        author = serializer.validated_data.get('author')
        user = serializer.validated_data.get('user')
        if author == user:
            raise ValidationError('Нельзя подписываться на самого себя')
        try:
            Subscription.objects.get(author=author, user=user)
            raise ValidationError('Подписка уже оформлена')
        except Subscription.DoesNotExist:
            serializer.save(author=author)
        return Response(
            status=status.HTTP_201_CREATED,
            data=serializer.data
        )

    def destroy(self, request, author_id=None):
        user = request.user
        author_obj = get_object_or_404(User, id=author_id)

        try:
            instance = Subscription.objects.get(
                user=user,
                author=author_obj
            )
        except Subscription.DoesNotExist:
            raise ValidationError('Вы не подписаны на этого пользователя')
        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class FavouritesViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavouritesSerializer

    def create(self, request, recipe_id=None):
        serializer = self.serializer_class(
            data=request.data, context={
                'request': request, 'recipe_id': recipe_id
            }
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        recipe = serializer.validated_data.get('recipe')
        try:
            Favourites.objects.get(user=user, recipe=recipe)
            raise ValidationError('Рецепт уже есть в избранном')
        except Favourites.DoesNotExist:
            serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
            data=serializer.data
        )

    def destroy(self, request, recipe_id=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)

        try:
            instance = Favourites.objects.get(
                user=user,
                recipe=recipe
            )
        except Favourites.DoesNotExist:
            raise ValidationError('Этого рецепта нет в избранном')
        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class ShoppingCartViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        return Shopping_cart.objects.filter(user=self.request.user)

    def create(self, request, recipe_id=None):
        serializer = self.serializer_class(
            data=request.data, context={
                'request': request, 'recipe_id': recipe_id
            }
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        recipe = serializer.validated_data.get('recipe')
        try:
            Shopping_cart.objects.get(user=user, recipe=recipe)
            raise ValidationError('Рецепт уже есть в списке покупок')
        except Shopping_cart.DoesNotExist:
            serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
            data=serializer.data
        )

    def destroy(self, request, recipe_id=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)

        try:
            instance = Shopping_cart.objects.get(
                user=user,
                recipe=recipe
            )
        except Shopping_cart.DoesNotExist:
            raise ValidationError('Этого рецепта нет в списке покупок')
        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def list(self, request):
        qset = self.get_queryset()
        sum_amount_for_ingr = {}

        # Наполняю словарь с id ингредиентов и общее количество для каждого
        for obj in qset:
            ingredients_amounts = obj.recipe.ingredients.all()
            for obj in ingredients_amounts:
                ingr_id = str(obj.ingredient_id)
                if ingr_id in sum_amount_for_ingr:
                    sum_amount_for_ingr[ingr_id]['amount'] += obj.amount
                    continue
                sum_amount_for_ingr[ingr_id] = {'amount': obj.amount}

        # Добавляю информацию о имени и единице измерения
        ingredients = Ingredient.objects.filter(
            id__in=sum_amount_for_ingr.keys()
        )
        for ingr in ingredients:
            ingr_id = str(ingr.id)
            sum_amount_for_ingr[ingr_id]['measurement_unit'] = ingr.measurement_unit  # noqa E501
            sum_amount_for_ingr[ingr_id]['name'] = ingr.name

        # Перевожу информацию в строку
        text = ''

        for id in sum_amount_for_ingr:
            ingr_info = sum_amount_for_ingr[id]
            text += f'{ingr_info["name"]} ({ingr_info["measurement_unit"]}) — {ingr_info["amount"]}\n'  # noqa E501

        # Строку перевожу в байты на вывод
        file_as_bytes = str.encode(text)

        response = HttpResponse(file_as_bytes)
        return response
