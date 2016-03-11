from rest_framework.pagination import PageNumberPagination


class ProfilePagination(PageNumberPagination):
    page_size = 20
