import os
from typing import List

from khl import Message, MessageTypes
from .plugin_interface import PluginInterface
from .type.plugin import Plugin
from ..config.config import Config


class PluginManager:

    plugins: List[Plugin]

    def __init__(self, config: Config) -> None:
        self.plugins = []
        self.config = config
        self.interface = PluginInterface(self)
        self.interface.bot.client.register(MessageTypes.TEXT, self.on_message)

    def search_all_plugin(self):
        self.plugins.clear()
        self.plugins.append(Plugin('khl.plugin.builtin.khl_plugin'))
        for DIR in self.config.plugin_directories:
            file_list = os.listdir(DIR)
            for file in file_list:
                if file.endswith('.py'):
                    self.plugins.append(Plugin(f'{DIR}.{file.replace(".py", "")}'))

    def load_plugins(self):
        self.search_all_plugin()
        for plugin in self.plugins:
            plugin.on_load(self.interface)

    def unload_plugins(self):
        for plugin in self.plugins:
            plugin.on_unload(self.interface)

    async def on_message(self, msg: Message):
        for plugin in self.plugins:
            await plugin.on_message(msg)
