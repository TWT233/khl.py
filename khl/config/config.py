from typing import List


class Config:

    token: str
    plugin_directories: List[str]

    def __init__(self, **kwargs) -> None:
        self.token = kwargs.get('token', '')
        self.plugin_directories = kwargs.get('plugin_directories', '')
