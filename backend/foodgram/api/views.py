from .mixins import ExcludeUpdate_ModelViewSet


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
