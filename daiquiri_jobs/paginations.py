from rest_framework.pagination import PageNumberPagination


class JobPagination(PageNumberPagination):
    page_size = 20
