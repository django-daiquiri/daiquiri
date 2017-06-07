from rest_framework.pagination import PageNumberPagination


class ListPagination(PageNumberPagination):
    page_size = 30
