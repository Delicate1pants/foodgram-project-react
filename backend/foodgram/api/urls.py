from django.urls import include, path
from djoser.views import TokenDestroyView as DjoserTokenDestroyView
from rest_framework import routers

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet, TokenCreateView)

app_name = 'api'

router = routers.SimpleRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
# router.register(
#     r'users/subscriptions',
#     SubscriptionViewSet, basename='subscriptions'
# )
# router.register(
#     r'users/(?P<author_id>\d+)/subscribe',
#     SubscriptionViewSet, basename='subscribe'
# )

urlpatterns = [
    path(
        'v1/users/subscriptions/',
        SubscriptionViewSet.as_view({'get': 'list'}),
        name='sub-list'
    ),
    path(
        'v1/users/<int:pk>/subscribe/',
        SubscriptionViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='sub-detail'
    ),
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/auth/token/login/', TokenCreateView.as_view()),
    path('v1/auth/token/logout/', DjoserTokenDestroyView.as_view()),
]
