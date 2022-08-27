from django.db.models import Q, Sum
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
from .mixins import CustomCreateModelMixin, CustomDestroyModelMixin
from .pagination import ListPagination
from .permissions import HasAccessOrReadOnly
from .serializers import (FavouritesSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer)
from recipes.models import (Favourite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
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

    pagination_class = None


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
        pagination = ListPagination()
        final_qs = pagination.paginate_queryset(
            queryset=self.get_queryset(), request=request
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
        serializer.save()
        return Response(
            status=status.HTTP_201_CREATED,
            data=serializer.data
        )

    def destroy(self, request, author_id=None):
        user = request.user
        author_obj = get_object_or_404(User, id=author_id)

        if Subscription.objects.filter(
                user=user,
                author=author_obj
        ).exists():
            instance = Subscription.objects.get(
                user=user,
                author=author_obj
            )
            instance.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        raise ValidationError('Вы не подписаны на этого пользователя')


class FavouritesViewSet(
    CustomCreateModelMixin,
    CustomDestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavouritesSerializer
    related_model = Favourite
    delete_error_msg = 'Этого рецепта нет в избранном'

    def destroy(
        self, request, related_model=None, delete_error_msg=None,
        recipe_id=None
    ):
        return super().destroy(
            request, self.related_model, self.delete_error_msg, recipe_id
        )


class ShoppingCartViewSet(
    CustomCreateModelMixin,
    CustomDestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    serializer_class = ShoppingCartSerializer
    related_model = ShoppingCart
    delete_error_msg = 'Этого рецепта нет в списке покупок'

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def destroy(
        self, request, related_model=None, delete_error_msg=None,
        recipe_id=None
    ):
        return super().destroy(
            request, self.related_model, self.delete_error_msg, recipe_id
        )

    def list(self, request):
        qset = self.get_queryset()

        recipe_ids = qset.values_list('recipe_id', flat=True)

        ingredient_amounts_ids = Recipe.objects.filter(
            id__in=recipe_ids
        ).values('ingredients')

        ingredient_ids = IngredientAmount.objects.filter(
            primary_key__in=ingredient_amounts_ids
        ).values('ingredient_id')

        ingredients_info = Ingredient.objects.filter(
            id__in=ingredient_ids
        ).annotate(amount=Sum('ingredients__amount', filter=Q(
            ingredients__primary_key__in=ingredient_amounts_ids)
        )).values('name', 'amount', 'measurement_unit')

        # Перевожу информацию в строку
        text = ''

        for obj in ingredients_info:
            name = obj['name'].capitalize()
            text += f'{name} ({obj["measurement_unit"]}) — {obj["amount"]}\n'

        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment;'
        )
        return response
