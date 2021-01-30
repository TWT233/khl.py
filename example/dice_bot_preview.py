import logging
import sys
sys.path.append('.')
import json

from khl import Cert, Bot, TextMsg

# load config from config/config.json,
# replace `path` points to your own config file.
#
# config template: `./config/config.json.example`
# rename it into 'config.json' and filling fields
with open('./example/config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Cert for Bot OAuth and data decrypt
# pass `verify_token` to `Cert()` to get a webhook cert
# besides you can pass `type=Cert.Types.WH` explicitly to get a webhook cert
# meanwhile `type=Cert.Types.WS` will gain a websocket cert
cert = Cert(client_id=config['client_id'],
            client_secret=config['client_secret'],
            token=config['token'])

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
bot = Bot(cmd_prefix=['.', '。'], cert=cert)
logging.basicConfig(level=logging.DEBUG)


# add command, accept optional arguments
# you can invoke this command via:
#   `.echo test`
@bot.command(name='echo')
async def func(msg: TextMsg, *args: str):
    logging.info(await msg.ctx.send(f'{args}'))
    return None

logging.debug('ready to run')

# everything done, go ahead now!
bot.run()
