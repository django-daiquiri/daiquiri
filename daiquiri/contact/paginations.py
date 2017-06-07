from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    page_size = 30
