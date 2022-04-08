import contextlib
import importlib

from .meta import Meta


class Plugin:

    def __init__(self, path: str) -> None:
        self.module = importlib.import_module(path)
        self.meta = Meta(self.module)

        with contextlib.suppress(Exception):
            self.on_load = self.module.on_load
        with contextlib.suppress(Exception):
            self.on_unload = self.module.on_unload
        with contextlib.suppress(Exception):
            self.on_message = self.module.on_message

    def __str__(self) -> str:
        return self.meta.name
