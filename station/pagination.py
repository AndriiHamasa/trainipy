from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class StationLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 25

