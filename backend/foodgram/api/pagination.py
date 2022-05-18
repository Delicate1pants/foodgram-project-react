from rest_framework.pagination import PageNumberPagination


class UserListPagination(PageNumberPagination):
    page_size_query_param = 'limit'
