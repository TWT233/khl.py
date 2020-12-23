import json
import random

from khl import TextMsg
from khl.webhook import Bot, Cert

# load config from config/config.json, replace `path` points to your own config file
# config template: `./config/config.json`
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Cert for Bot OAuth and data decrypt
# literal param passing
cert = Cert(client_id=config['client_id'], client_secret=config['client_secret'],
            token=config['token'], verify_token=config['verify_token'],
            encrypt_key='encrypt_key' in config.keys() and config['encrypt_key'] or '')

# init Bot
# set `compress` param corresponding to your webhook callback url
# use port 5000 and route `/khl-wh` in default
# can manually set port now, while route is fixed(will feat in shortly)
# so remember to append `:5000/khl-wh` to callback url
# i.e:
#                callback url                   |          construct call           |
#       http://your.domain:5000/khl-wh          |   Bot(cert=cert, compress=True)   |   (explicitly enable compress)
#  http://your.domain:5000/khl-wh?compress=0    |   Bot(cert=cert, compress=False)  |   (disable compress)
#          http://your.domain:2333              |      Bot(cert=cert, port=2333)    |   (set port)
#       http://your.domain:5000/khl-wh          |          Bot(cert=cert)           |   (all as default)
bot = Bot(cert=cert, cmd_prefix=['!', '！'], compress=True)


# add command, accept optional arguments
# you can invoke this command via:`!骰子 1 100` or ``
@bot.command(name='骰子')
async def roll(msg: TextMsg, r_min: str, r_max: str, n: str = 1):
    await bot.send(msg.target_id, f'骰出来了：{[random.randint(int(r_min), int(r_max)) for i in range(int(n))]}')


# everything done, go ahead now!
bot.run()
