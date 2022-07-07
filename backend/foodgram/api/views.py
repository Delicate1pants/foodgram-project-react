from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import utils
from djoser.conf import settings
from djoser.views import TokenCreateView as DjoserTokenCreateView
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filtersets import RecipeFilterSet
from .pagination import IngredientListPagination, RecipeListPagination
from .permissions import HasAccessOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)
from recipes.models import Ingredient, Recipe, Tag
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
    pagination_class = RecipeListPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SubscriptionViewSet(
    viewsets.ViewSet
):
    permission_classes = (IsAuthenticated,)

    def list(*args, **kwargs):
        pass

    def create(*args, **kwargs):
        pass

    def destroy(self, request, pk=None):
        user = request.user
        author_obj = get_object_or_404(User, id=pk)

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


class ActualSubscriptionViewSet(SubscriptionViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def perform_create(self, serializer):
        author_id = self.kwargs.get('author_id')
        author = get_object_or_404(User, id=author_id)
        user = self.request.user
        if author == user:
            raise ValidationError('Нельзя подписываться на самого себя')
        try:
            Subscription.objects.get(author=author, user=user)
            raise ValidationError('Подписка уже оформлена')
        except Subscription.DoesNotExist:
            serializer.save(author=author)
