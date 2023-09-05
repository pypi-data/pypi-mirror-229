import logging

from django.core.cache import BaseCache, InvalidCacheBackendError, caches

from request_pressure_tracker.notifier_locks.base import BaseNotifierLock

logger = logging.getLogger('django.time_in_queue')


class DjangoCacheNotifierLock(BaseNotifierLock):
    def __init__(
            self,
            lock_name: str,
            cache_name: str = 'default',
    ):
        self.cache_name = cache_name
        super().__init__(lock_name)

    def get_cache(self) -> BaseCache:
        try:
            return caches[self.cache_name]
        except InvalidCacheBackendError:
            logger.warning('Bad cache {0} defined. Using default'.format(self.cache_name))
            return caches['default']

    def lock(self) -> bool:
        cache_instance = self.get_cache()
        if cache_instance.has_key(self.lock_name):
            return False

        cache_instance.set(self.lock_name, True, 60)
        return True

    def unlock(self):
        cache_instance = self.get_cache()
        cache_instance.delete(self.lock_name)
