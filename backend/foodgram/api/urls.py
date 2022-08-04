from django.urls import include, path
from djoser.views import TokenDestroyView as DjoserTokenDestroyView
from rest_framework import routers

from .views import (FavouritesViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, SubscriptionViewSet, TagViewSet,
                    TokenCreateView)

app_name = 'api'

router = routers.SimpleRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionViewSet.as_view({'get': 'list'}),
        name='sub-list'
    ),
    path(
        'users/<int:author_id>/subscribe/',
        SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='sub-detail'
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavouritesViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartViewSet.as_view({'get': 'list'}),
        name='download_shopping_cart'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', TokenCreateView.as_view(), name='token_create'),
    path(
        'auth/token/logout/', DjoserTokenDestroyView.as_view(),
        name='token_destroy'
    ),
]
