import json

from khl import TextMsg, Bot, Cert, Msg, MessageRule

# load config from config/config.json, replace `path` points to your own config file
# config template: `./config/config.json.example`
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# init Cert for Bot OAuth
cert = Cert(client_id=config['client_id'],
            client_secret=config['client_secret'],
            token=config['token'])

# init Bot
bot = Bot(cmd_prefix=['!', '！'], cert=cert)


async def simple_rule(msg: Msg, *args) -> bool:
    if msg.content.find("bot"):
        return True
    return False


# register command
# invoke this via saying `!hello` in channel
# but there will be no reply
@bot.command(name='hello', rule=simple_rule)
async def roll(msg: TextMsg, *args):
    await msg.reply(f'hello')


# now you can send "!hello zhangsan bot"


# please at your bot
async def angry_bot(msg: TextMsg, *args):
    await msg.reply(f'dont at me!')


bot.on_text_msg(angry_bot, rule=MessageRule.at_me())

# everything done, go ahead now!

bot.run()
