import json
import random

from khl import TextMsg, Bot, Cert

# load config from config/config.json, replace `path` points to your own config file
# config template: `./config/config.json`
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Cert for Bot OAuth and data decrypt
# pass `verify_token` to `Cert()` to get a webhook cert
# besides you can pass `type='webhook'` explicitly to get a webhook cert
# meanwhile `type='websocket'` will gain a websocket cert
cert = Cert(
    client_id=config['client_id'],
    client_secret=config['client_secret'],
    token=config['token'],
    verify_token=config['verify_token'],
    encrypt_key='encrypt_key' in config.keys() and config['encrypt_key'] or '')

# init Bot
# set `compress`, `port`, `route` params corresponding to your webhook callback url
# use compress enabled, port 5000, route `/khl-wh` in default
# i.e:
#                callback url                   |         constructor call          |
#       http://your.domain:5000/khl-wh          |          Bot(cert=cert)           |   (all in default)
#   http://your.domain:5000/khl-wh?compress=0   |   Bot(cert=cert, compress=False)  |   (disable compress)
#          http://your.domain:2333              |      Bot(cert=cert, port=2333)    |   (set port)
#        http://your.domain:5000/meow           |   Bot(cert=cert, route='/meow')   |   (set route)
bot = Bot(cmd_prefix=['!', '！'], cert=cert, port=2333, compress=False, route='/meow')


# add command, accept optional arguments
# you can invoke this command via:
#   `!roll 1 100`
#   `!roll 1 100 3` (param `n` is optional as set below)
@bot.command(name='roll')
async def roll(msg: TextMsg, r_min: str, r_max: str, n: str = 1):
    await bot.send(
        msg.target_id,
        f'you got：{[random.randint(int(r_min), int(r_max)) for i in range(int(n))]}'
    )


# everything done, go ahead now!
bot.run()
