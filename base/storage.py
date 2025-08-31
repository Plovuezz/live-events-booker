import os

from django.core.cache import cache
from storages.backends.dropbox import DropboxStorage
from storages.utils import safe_join


class WindowsCompatibleDropboxStorage(DropboxStorage):
    CACHE_TTL = 60 * 60 * 4 - 10

    def _full_path(self, name):
        if name == "/":
            name = ""

        # If the machine is windows do not append the drive letter to file path
        if os.name == "nt":
            return os.path.join("/", self.root_path, name).replace("\\", "/")
        else:
            return safe_join(self.root_path, name).replace("\\", "/")

    @staticmethod
    def _get_cache_key(name: str) -> str:
        return f"dropbox:media:{name}"

    def url(self, name):
        cache_key = self._get_cache_key(name)

        if link := cache.get(cache_key):
            return link

        link = super().url(name)
        cache.set(cache_key, link, self.CACHE_TTL)

        return link

    # def _save(self, name, content):
    #     name = super()._save(name, content)
    #
    #     link = self.client.sharing_create_shared_link(self._full_path(name))
    #     url = link.url.replace("dl=0", "dl=1")
    #
    #     return url
    #
    # def url(self, name):
    #     return name