import json
import random

from khl import TextMsg, Bot, Cert
import khl

# load config from config/config.json, replace `path` points to your own config file
# config template: `./config/config.json`
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Cert for Bot OAuth
cert = Cert(client_id=config['client_id'],
            client_secret=config['client_secret'],
            token=config['token'])

# init Bot
bot = Bot(cmd_prefix=['!', '！'], cert=cert)


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


@bot.command(name='dd')
async def dd(msg: TextMsg):
    card = [{
        "type":
        "card",
        "theme":
        "secondary",
        "size":
        "lg",
        "modules": [{
            "type":
            "action-group",
            "elements": [{
                "type": "button",
                "theme": "primary",
                "value": "ok",
                "click": "return-val",
                "text": {
                    "type": "plain-text",
                    "content": "确定"
                }
            }]
        }]
    }]
    rsp = await msg.reply_card(card)
    res = await msg.ctx.wait_btn(rsp['msg_id'])
    await msg.reply(f'{res}')


# add event listener
# now support: on_text_msg, on_all_msg, on_system_msg
@bot.on_text_msg
async def greeter(msg: TextMsg):
    if (msg.content == 'hello'):
        await bot.send(msg.target_id, f'hi')


khl.Logger.enable_debug()
# everything done, go ahead now!
bot.run()
