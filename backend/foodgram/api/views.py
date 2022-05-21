from djoser import utils
from djoser.conf import settings
from djoser.views import TokenCreateView as DjoserTokenCreateView
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .mixins import ExcludeUpdate_ModelViewSet
from .pagination import IngredientListPagination
from .serializers import IngredientSerializer, TagSerializer
from recipes.models import Ingredient, Tag


class TokenCreateView(DjoserTokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)

    pagination_class = IngredientListPagination


class TagViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewset(ExcludeUpdate_ModelViewSet):
    pass
    # serializer_class = 'RecipeSerializer'
    # permission_classes = ('HasAccessOrReadOnly',)
    # pagination_class = 'PageNumberPagination'

    # filter_backends = ['SearchFilter or DjangoFilterBackend?']
    # filterset_class = '?'
    # search_fields = ('something',)
    # search_fields = ['=something', ]

    # queryset = '?'

    # lookup_field = '?'
