from django.urls import include, path
from djoser.views import TokenDestroyView as DjoserTokenDestroyView
from rest_framework import routers

from .views import TokenCreateView

app_name = 'api'

router = routers.SimpleRouter()
# router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    # path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/auth/token/login/', TokenCreateView.as_view()),
    path('v1/auth/token/logout/', DjoserTokenDestroyView.as_view()),
]
