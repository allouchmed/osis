##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import abc
import logging
from functools import wraps

from django.conf import settings
from django.core.cache import caches, InvalidCacheBackendError
from django.http import QueryDict

CACHE_FILTER_TIMEOUT = None
PREFIX_CACHE_KEY = 'cache_filter'

logger = logging.getLogger(settings.DEFAULT_LOGGER)
try:
    cache = caches["redis"]
except InvalidCacheBackendError:
    logger.warning("Rolled back to default cache")
    cache = caches["default"]


def cache_filter(exclude_params=None, **default_values):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            try:
                request_cache = RequestCache(user=request.user, path=request.path)
                if request.GET:
                    request_cache.save_get_parameters(request, parameters_to_exclude=exclude_params)
                request.GET = request_cache.restore_get_request(request, **default_values)
            except Exception:
                logger.exception('An error occurred with cache system')
            return func(request, *args, **kwargs)

        return inner

    return decorator


class CacheFilterMixin:
    cache_exclude_params = None

    # Mixin that keep the cache for cbv.
    def get(self, request, *args, **kwargs):
        request_cache = RequestCache(user=request.user, path=request.path)
        if request.GET:
            request_cache.save_get_parameters(request, parameters_to_exclude=self.cache_exclude_params)
        request.GET = request_cache.restore_get_request(request)
        return super().get(request, *args, **kwargs)


class OsisCache(abc.ABC):
    PREFIX_KEY = None

    @abc.abstractmethod
    def key(self):
        return self.PREFIX_KEY

    @property
    def cached_data(self):
        return cache.get(self.key)

    def set_cached_data(self, data, timeout=None):
        cache.set(self.key, data, timeout=timeout)

    def clear(self):
        cache.delete(self.key)


class RequestCache(OsisCache):
    PREFIX_KEY = 'cache_filter'

    def __init__(self, user, path):
        self.user = user
        self.path = path

    @property
    def key(self):
        return "_".join([self.PREFIX_KEY, str(self.user.id), self.path])

    def save_get_parameters(self, request, parameters_to_exclude=None):
        parameters_to_exclude = parameters_to_exclude or []
        param_to_cache = {key: value for key, value in request.GET.items() if key not in parameters_to_exclude}
        self.set_cached_data(param_to_cache)

    def restore_get_request(self, request, **default_values):
        cached_value = self.cached_data or default_values

        new_get_request = QueryDict(mutable=True)
        new_get_request.update({**request.GET.dict(), **cached_value})

        return new_get_request


class ElementCache(OsisCache):
    PREFIX_KEY = 'select_element_{user}'

    def __init__(self, user):
        self.user = user

    @property
    def key(self):
        return self.PREFIX_KEY.format(user=self.user.pk)

    def save_element_selected(self, obj):
        data_to_cache = {'id': obj.pk, 'modelname': obj._meta.db_table}
        self.set_cached_data(data_to_cache)
