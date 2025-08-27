import os

from django.core.cache import cache
from storages.backends.dropbox import DropboxStorage
from storages.utils import safe_join


# class WindowsCompatibleDropboxStorage(DropboxStorage):
#     CACHE_TTL = 60 * 60 * 2
#
#     @staticmethod
#     def _get_cache_key(name: str) -> str:
#         return f"dropbox:media:{name}"
#
#     def url(self, name):
#         cache_key = self._get_cache_key(name)
#
#         if link := cache.get(cache_key):
#             return link
#
#         link = super().url(name)
#         cache.set(cache_key, link, self.CACHE_TTL)
#
#         return link
