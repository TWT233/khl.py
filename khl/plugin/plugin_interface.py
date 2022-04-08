from ..bot import Bot

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .plugin_manager import PluginManager


class PluginInterface:
    def __init__(self, plg_manager: 'PluginManager') -> None:
        self.plugin_Manager = plg_manager
        self.config = self.plugin_Manager.config
        self.bot = Bot(self.config.token)
        self.help_messages = {}

    def registry_help_messages(self, prefix: str, desc: str):
        self.help_messages[prefix] = desc
