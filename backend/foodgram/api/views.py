from djoser import utils
from djoser.conf import settings
from djoser.views import TokenCreateView as DjoserTokenCreateView
from rest_framework import status
from rest_framework.response import Response

from .mixins import ExcludeUpdate_ModelViewSet


class TokenCreateView(DjoserTokenCreateView):
    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED
        )


class RecipeViewSet(ExcludeUpdate_ModelViewSet):
    serializer_class = 'RecipeSerializer'
    permission_classes = ('HasAccessOrReadOnly',)
    pagination_class = 'PageNumberPagination'

    filter_backends = ['SearchFilter or DjangoFilterBackend?']
    filterset_class = '?'
    search_fields = ('something',)
    search_fields = ['=something', ]

    queryset = '?'

    lookup_field = '?'
