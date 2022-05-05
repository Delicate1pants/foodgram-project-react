from django.urls import include, path
from rest_framework import routers

from .views import RecipeViewSet

app_name = 'api'

router = routers.SimpleRouter()
# router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    # path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
]
