
from rest_framework.pagination import PageNumberPagination


class ExamplePagination(PageNumberPagination):
    page_size = 20
