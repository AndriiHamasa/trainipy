from rest_framework.pagination import LimitOffsetPagination


class StationLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5
    # limit_query_param = "limit"
    max_limit = 25