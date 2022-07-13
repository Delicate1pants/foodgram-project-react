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
                          RecipeSerializer, SubscriptionSerializer,
                          TagSerializer)
from recipes.models import Favourites, Ingredient, Recipe, Tag
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

    queryset = Recipe.objects.all()
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
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeLimitFilterSet

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = Subscription.objects.filter(user=request.user)
        pagination = ListPagination()
        # filtered_qs = self.filter_queryset(queryset=queryset)
        final_qs = pagination.paginate_queryset(
            queryset=queryset, request=request
        )
        serializer = self.serializer_class(
            final_qs, many=True, context={
                'request': request,
                # Фильтровать буду в сериализаторе,
                # с SerializerMethodField так удобнее
                'recipes_limit': self.request.query_params.get('recipes_limit')
            }
        )
        return pagination.get_paginated_response(
            data=serializer.data
        )

    def create(self, request, author_id=None):
        serializer = self.serializer_class(
            data=request.data, context={
                'request': request, 'author_id': author_id
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
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = RecipeLimitFilterSet

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
