import json
from khl.command_preview.typings.types import BaseSession
import random

from khl import Cert
from khl.bot_preview import BotPreview
from khl.command_preview import AppCommand

# load config from config/config.json,
# replace `path` points to your own config file.
#
# config template: `./config/config.json.example`
# rename it into 'config.json' and filling fields
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Cert for Bot OAuth and data decrypt
# pass `verify_token` to `Cert()` to get a webhook cert
# besides you can pass `type=Cert.Types.WH` explicitly to get a webhook cert
# meanwhile `type=Cert.Types.WS` will gain a websocket cert
cert = Cert(
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    token=config['token'],
    verify_token=config['verify_token'],
    encrypt_key='encrypt_key' in config.keys() and config['encrypt_key'] or '')

# init Bot
# set params `compress`, `port`, `route` corresponding to your webhook
# callback url.
# use compress=enabled, port=5000, route='/khl-wh' in default
# i.e:
#              callback url                 |       constructor call
#     http://your.domain:5000/khl-wh        |        Bot(cert=cert)
# http://your.domain:5000/khl-wh?compress=0 | Bot(cert=cert, compress=False)
#        http://your.domain:2333            |    Bot(cert=cert, port=2333)
#      http://your.domain:5000/meow         | Bot(cert=cert, route='/meow')
bot = BotPreview(port=2000, cmd_prefix=['.', '。'], cert=cert)


# add command, accept optional arguments
# you can invoke this command via:
#   `!roll 1 100`
#   `!roll 1 100 3` (param `n` is optional as set below)
class DiceApp(AppCommand):
    trigger = 'roll'

    async def func(self, session: BaseSession):
        r_min, r_max, n = session.args
        n = n if n else 1
        return session.reply(
            f'you got：{[random.randint(int(r_min), int(r_max)) for i in range(int(n))]}'
        )


bot.add_command(DiceApp())

# everything done, go ahead now!
bot.run()
