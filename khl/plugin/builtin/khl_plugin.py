from khl import Message

from khl.plugin.plugin_interface import PluginInterface

PLUGIN_METADATA = {
    'id': 'khl_plugin',
    'version': '1.0.0',
    'name': 'KHL Plugin',
    'description': 'A khl.py builtin plugin',
    'author': 'DancingSnow',
    'link': 'https://github.com/DancingSnow0517/khl.py/tree/plugin'
}


def on_load(interface: PluginInterface):
    bot = interface.bot

    interface.registry_help_messages('!!help', '显示帮助信息')
    interface.registry_help_messages('!!khl', '显示机器人信息')

    @bot.command(name='help', prefixes=['!!'])
    async def help_msg(msg: Message):
        help_messages = ''
        for i in interface.help_messages:
            help_messages += f'[{i}] {interface.help_messages[i]}\n'
        await msg.reply(help_messages)

    @bot.command(name='khl', prefixes=['!!'])
    async def khl(msg: Message):
        rt = f'当前已加载 {len(interface.plugin_Manager.plugins)} 个插件'
        await msg.reply(rt)


# run when bot stop
def on_unload(interface: PluginInterface):
    pass


# run when a message is received
async def on_message(msg: Message):
    pass
