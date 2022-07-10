from rest_framework.pagination import PageNumberPagination


class ListPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class IngredientListPagination(PageNumberPagination):
    # Пагинация не определена спецификацией, но 2188 объект при выдаче
    # всех ингредиентов - это слишком, я думаю
    page_size = 50
