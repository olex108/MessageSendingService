from typing import Callable
from functools import wraps

from django.core.cache import cache


def get_cache_cotext_for_user(page: str) -> Callable:
    """
    Function decorator for caching context data for pages of user.
    function get or set cache with page name and id of user in form 'page/id',
    for cache delete data with key: view from context

    :param page: name of page
    """

    def wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            user = self.request.user
            if user:
                queryset = cache.get(f"{page}/{user.id}")
                if queryset is None:
                    queryset = func(self, *args, **kwargs)
                    view = queryset.pop("view")
                    cache.set(f"{page}/{user.id}", queryset, 60 * 15)
                    queryset["view"] = view
                    return queryset
            else:
                queryset = func(self, *args, **kwargs)
            return queryset
        return inner
    return wrapper


def get_cache_queryset_for_user(page: str) -> Callable:
    """
        Function decorator for caching queryset for pages of user.
        function get or set cache with page name and id of user in form 'page/id'

        :param page: name of page
    """

    def wrapper(func):
        @wraps(func)
        def inner(self, *args, **kwargs):
            user = self.request.user
            if user:
                queryset = cache.get(f"{page}/{user.id}")
                if queryset is None:
                    queryset = func(self, *args, **kwargs)
                    cache.set(f"{page}/{user.id}", queryset, 60 * 15)
                    return queryset
            else:
                queryset = func(self, *args, **kwargs)
            return queryset
        return inner
    return wrapper
